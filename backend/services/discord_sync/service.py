import asyncio
import hashlib
from sqlalchemy import select, delete
from core.db import get_sessionmaker
from core.logging import get_logger
from models.db_models import Category, DiscordSyncChannel, DiscordSyncedGuide, Guide, SystemSetting
from services.common.media import MediaService
from services.common.telegram_notify import telegram_notify_service
from services.discord_sync.translator import sanitize_discord_markdown, translate_en_to_ru, generate_tldr_block

logger = get_logger("blackrose.services.discord_sync")

class DiscordSyncService:
    @classmethod
    async def get_setting(cls, key: str) -> str | None:
        try:
            async with get_sessionmaker()() as session:
                res = await session.execute(select(SystemSetting.value).where(SystemSetting.key == key))
                return res.scalar_one_or_none()
        except Exception as e:
            logger.warning(f"Error fetching system setting {key}: {e}")
            return None

    @classmethod
    async def set_setting(cls, key: str, value: str | None) -> None:
        try:
            async with get_sessionmaker()() as session:
                res = await session.execute(select(SystemSetting).where(SystemSetting.key == key))
                setting = res.scalar_one_or_none()
                if not setting:
                    setting = SystemSetting(key=key, value=value)
                    session.add(setting)
                else:
                    setting.value = value
                await session.commit()
        except Exception as e:
            logger.error(f"Error setting system setting {key}: {e}")

    @classmethod
    async def get_all_channels(cls) -> list[dict]:
        async with get_sessionmaker()() as session:
            res = await session.execute(select(DiscordSyncChannel))
            channels = res.scalars().all()
            return [
                {
                    "channel_id": c.channel_id,
                    "channel_name": c.channel_name,
                    "category_key": c.category_key,
                    "auto_translate": c.auto_translate,
                    "is_active": c.is_active,
                    "created_at": c.created_at.isoformat() if c.created_at else None,
                }
                for c in channels
            ]

    @classmethod
    async def add_channel(
        cls, channel_id: str, category_key: str, channel_name: str | None = None, auto_translate: bool = True
    ) -> dict:
        async with get_sessionmaker()() as session:
            # Check if category exists
            cat_res = await session.execute(select(Category).where(Category.key == category_key))
            if not cat_res.scalar_one_or_none():
                return {"error": "Указанная категория не существует"}

            res = await session.execute(
                select(DiscordSyncChannel).where(DiscordSyncChannel.channel_id == channel_id)
            )
            ch = res.scalar_one_or_none()
            if not ch:
                ch = DiscordSyncChannel(
                    channel_id=channel_id,
                    channel_name=channel_name or f"Channel-{channel_id}",
                    category_key=category_key,
                    auto_translate=auto_translate,
                    is_active=True,
                )
                session.add(ch)
            else:
                ch.category_key = category_key
                ch.channel_name = channel_name or ch.channel_name
                ch.auto_translate = auto_translate
                ch.is_active = True

            await session.commit()
            return {"ok": True, "channel_id": ch.channel_id}

    @classmethod
    async def remove_channel(cls, channel_id: str) -> bool:
        async with get_sessionmaker()() as session:
            await session.execute(
                delete(DiscordSyncChannel).where(DiscordSyncChannel.channel_id == channel_id)
            )
            await session.commit()
            return True

    @classmethod
    async def process_discord_message(cls, message_data: dict) -> dict:
        """
        Processes an incoming Discord message or thread payload.
        Checks target channel mapping, computes SHA-256 diff, sanitizes, translates, and upserts to DB.
        """
        channel_id = str(message_data.get("channel_id", ""))
        message_id = str(message_data.get("id", ""))
        raw_content = message_data.get("content", "")
        attachments = message_data.get("attachments", [])
        author_info = message_data.get("author", {})
        author_tag = f"{author_info.get('username', 'author')}#{author_info.get('discriminator', '0000')}" if author_info else "Discord Author"

        if not channel_id or not message_id or not raw_content.strip():
            return {"skipped": True, "reason": "empty content or missing channel/message id"}

        try:
            async with get_sessionmaker()() as session:
                # 1. Verify channel is tracked
                res = await session.execute(
                    select(DiscordSyncChannel).where(
                        DiscordSyncChannel.channel_id == channel_id,
                        DiscordSyncChannel.is_active,
                    )
                )
                config = res.scalar_one_or_none()
                if not config:
                    return {"skipped": True, "reason": f"channel {channel_id} is not configured for sync"}

                category_key = config.category_key
                auto_translate = config.auto_translate

                # Verify target category exists to prevent foreign key integrity errors
                cat_res = await session.execute(select(Category).where(Category.key == category_key))
                if not cat_res.scalar_one_or_none():
                    logger.warning(f"Category '{category_key}' does not exist in database. Skipping message.")
                    return {"skipped": True, "reason": f"category '{category_key}' does not exist"}

                # 2. SHA-256 hash check for diffing
                content_hash = hashlib.sha256(raw_content.encode("utf-8")).hexdigest()

            synced_res = await session.execute(
                select(DiscordSyncedGuide).where(DiscordSyncedGuide.discord_message_id == message_id)
            )
            existing_synced = synced_res.scalar_one_or_none()
            if existing_synced and existing_synced.content_hash == content_hash:
                return {"skipped": True, "reason": "content unchanged (hash match)"}

            # 3. Clean Discord Markdown & handle media
            clean_text = sanitize_discord_markdown(raw_content)

            # Download Discord attachments to local storage so URLs never expire
            local_photos: list[str] = []
            for att in attachments:
                url = att.get("url") if isinstance(att, dict) else str(att)
                if url:
                    try:
                        saved_path = await MediaService.import_from_url(url, folder=f"discord/{channel_id}")
                        if saved_path:
                            local_photos.append(saved_path)
                    except Exception as err:
                        logger.warning(f"Failed to import attachment {url}: {err}")

            # 4. Optional Translation (EN -> RU) & TL;DR block
            final_text = clean_text
            if auto_translate:
                final_text = await translate_en_to_ru(clean_text)
                final_text = generate_tldr_block(final_text)

            # 5. Extract Title
            first_line = clean_text.split("\n")[0].strip("# ").strip()
            title = first_line[:80] if first_line else f"Гайд от {author_tag}"

            # Key generation
            guide_key = existing_synced.guide_key if existing_synced else f"discord_{message_id}"

            # 6. Upsert into Guide table
            guide_res = await session.execute(select(Guide).where(Guide.key == guide_key))
            guide = guide_res.scalar_one_or_none()

            is_new_guide = guide is None

            if not guide:
                guide = Guide(
                    key=guide_key,
                    category_key=category_key,
                    title=title,
                    text=final_text,
                    photo=local_photos,
                    views=0,
                )
                session.add(guide)
            else:
                guide.title = title
                guide.text = final_text
                guide.category_key = category_key
                if local_photos:
                    guide.photo = local_photos

            # 7. Upsert into DiscordSyncedGuide tracker
            if not existing_synced:
                synced_record = DiscordSyncedGuide(
                    discord_message_id=message_id,
                    discord_channel_id=channel_id,
                    guide_key=guide_key,
                    content_hash=content_hash,
                    author_tag=author_tag,
                )
                session.add(synced_record)
            else:
                existing_synced.content_hash = content_hash
                existing_synced.author_tag = author_tag

            await session.commit()
            logger.info(f"Successfully synced Discord guide '{guide_key}' from channel {channel_id}")

            # Send Telegram broadcast notification if it's a new guide
            if is_new_guide:
                asyncio.create_task(
                    telegram_notify_service.send_guide_notification(
                        title=title,
                        category_key=category_key,
                        guide_key=guide_key,
                        author_tag=author_tag,
                    )
                )

            return {"ok": True, "guide_key": guide_key, "title": title}
        except Exception as err:
            logger.error(f"Error processing Discord message {message_id} in channel {channel_id}: {err}", exc_info=True)
            return {"skipped": True, "reason": str(err)}

    @classmethod
    async def get_synced_guides(cls, limit: int = 50) -> list[dict]:
        async with get_sessionmaker()() as session:
            res = await session.execute(
                select(DiscordSyncedGuide, Guide)
                .outerjoin(Guide, DiscordSyncedGuide.guide_key == Guide.key)
                .order_by(DiscordSyncedGuide.id.desc())
                .limit(limit)
            )
            items = []
            for synced, guide in res.all():
                items.append({
                    "id": synced.id,
                    "discord_message_id": synced.discord_message_id,
                    "discord_channel_id": synced.discord_channel_id,
                    "guide_key": synced.guide_key,
                    "author_tag": synced.author_tag,
                    "created_at": synced.created_at.isoformat() if synced.created_at else None,
                    "title": guide.title if guide else "Без названия",
                    "category_key": guide.category_key if guide else "uncategorized",
                    "views": guide.views if guide else 0,
                })
            return items


discord_sync_service = DiscordSyncService()
