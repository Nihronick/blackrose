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

def clean_guide_title(title: str, text: str, cat_key: str) -> str:
    import re
    t = (title or "").strip()
    # 1. If title starts with markdown image, emoji, or is corrupted
    if (
        t.startswith("![") 
        or t.startswith("!Скриншот") 
        or "{{" in t 
        or t.startswith("http") 
        or len(t) > 70
    ):
        candidate_lines = []
        for line in (text or "").split("\n"):
            clean_l = line.strip()
            if not clean_l:
                continue
            if (
                clean_l.startswith("![") 
                or clean_l.startswith("!Скриншот")
                or clean_l.startswith("{{") 
                or clean_l.startswith("http")
            ):
                continue
            candidate_lines.append(clean_l)
            
        if candidate_lines:
            t = candidate_lines[0]
        else:
            t = f"Гайд: {cat_key.replace('-', ' ').capitalize()}"

    # 2. Strip leftover markdown/emoji tags
    t = re.sub(r"!\[.*?(\]|\(|$).*?", "", t)
    t = re.sub(r"!Скриншот.*?", "", t)
    t = re.sub(r"\{\{.*?(\}\}|$)", "", t)
    t = re.sub(r"https?://\S+", "", t)
    t = re.sub(r"^#+\s*", "", t)
    t = re.sub(r"\*{1,3}(.*?)\*{1,3}", r"\1", t)
    t = t.strip()
    
    if not t or len(t) < 3:
        t = f"Гайд: {cat_key.replace('-', ' ').capitalize()}"
        
    return t


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
    async def process_discord_message(
        cls, message_data: dict, parent_channel_id: str | None = None, custom_title: str | None = None
    ) -> dict:
        """
        Processes an incoming Discord message or thread payload.
        Checks target channel mapping, computes SHA-256 diff, sanitizes, translates, and upserts to DB.
        """
        raw_channel_id = str(message_data.get("channel_id", ""))
        target_channel_id = parent_channel_id or raw_channel_id
        message_id = str(message_data.get("id", ""))
        raw_content = message_data.get("content", "")
        attachments = message_data.get("attachments", [])
        embeds = message_data.get("embeds", [])
        author_info = message_data.get("author", {})
        author_tag = f"{author_info.get('username', 'author')}#{author_info.get('discriminator', '0000')}" if author_info else "Discord Author"

        # Collect URLs from attachments
        attachments_urls: list[str] = []
        for att in attachments:
            if isinstance(att, dict):
                url = att.get("url") or att.get("proxy_url")
                if url:
                    attachments_urls.append(url)
            elif isinstance(att, str) and att:
                attachments_urls.append(att)

        # Collect URLs from embeds
        embed_photos: list[str] = []
        embed_videos: list[str] = []
        for emb in embeds:
            if isinstance(emb, dict):
                if emb.get("image") and emb["image"].get("url"):
                    embed_photos.append(emb["image"]["url"])
                if emb.get("thumbnail") and emb["thumbnail"].get("url"):
                    embed_photos.append(emb["thumbnail"]["url"])
                if emb.get("video") and emb["video"].get("url"):
                    embed_videos.append(emb["video"]["url"])
                if emb.get("url"):
                    e_url = emb["url"]
                    if any(e_url.lower().endswith(ext) for ext in (".png", ".jpg", ".jpeg", ".gif", ".webp")):
                        embed_photos.append(e_url)
                    elif any(e_url.lower().endswith(ext) for ext in (".mp4", ".webm", ".mov", ".mkv", ".gifv")) or "youtube.com" in e_url or "youtu.be" in e_url:
                        embed_videos.append(e_url)

        if not raw_content.strip():
            if attachments_urls or embed_photos or embed_videos:
                raw_content = f"Материалы гайда: {custom_title or 'Гайд'}"
            else:
                return {"skipped": True, "reason": "empty content and no media attachments"}

        if not target_channel_id or not message_id:
            return {"skipped": True, "reason": "missing channel or message id"}

        try:
            async with get_sessionmaker()() as session:
                # 1. Verify channel is tracked
                res = await session.execute(
                    select(DiscordSyncChannel).where(
                        DiscordSyncChannel.channel_id == target_channel_id,
                        DiscordSyncChannel.is_active,
                    )
                )
                config = res.scalar_one_or_none()
                if not config:
                    return {"skipped": True, "reason": f"channel {target_channel_id} is not configured for sync"}

                category_key = config.category_key
                auto_translate = config.auto_translate

                # Verify target category exists; fallback gracefully if missing
                cat_res = await session.execute(select(Category).where(Category.key == category_key))
                if not cat_res.scalar_one_or_none():
                    first_cat_res = await session.execute(select(Category).limit(1))
                    first_cat = first_cat_res.scalar_one_or_none()
                    if first_cat:
                        category_key = first_cat.key
                    else:
                        category_key = "general"

                # 2. SHA-256 hash check for diffing
                content_hash = hashlib.sha256(raw_content.encode("utf-8")).hexdigest()

                synced_res = await session.execute(
                    select(DiscordSyncedGuide).where(DiscordSyncedGuide.discord_message_id == message_id)
                )
                existing_synced = synced_res.scalar_one_or_none()
                if existing_synced and existing_synced.content_hash == content_hash:
                    return {"skipped": True, "reason": "content unchanged (hash match)"}

                # 3. Clean Discord Markdown & handle media
                clean_text, extracted_photos, extracted_videos = sanitize_discord_markdown(raw_content)

                all_media_candidates = list(dict.fromkeys(attachments_urls + extracted_photos + embed_photos + extracted_videos + embed_videos))
                video_extensions = ('.mp4', '.webm', '.mov', '.mkv', '.avi', '.flv', '.wmv', '.gifv')

                photo_candidates = []
                video_candidates = []

                for m_url in all_media_candidates:
                    if not m_url:
                        continue
                    clean_u = m_url.lower().split("?")[0]
                    if any(clean_u.endswith(ext) for ext in video_extensions) or "youtube.com" in clean_u or "youtu.be" in clean_u:
                        video_candidates.append(m_url)
                    else:
                        photo_candidates.append(m_url)

                # Download Discord attachments and extracted photos to persistent storage so URLs never expire
                local_photos: list[str] = []
                for url in photo_candidates:
                    try:
                        saved_path = await MediaService.import_from_url(url, folder=f"discord/{target_channel_id}")
                        if saved_path:
                            local_photos.append(saved_path)
                    except Exception as err:
                        logger.warning(f"Failed to import photo {url}: {err}")
                        local_photos.append(url)

                # Download and persist video files if they are direct video uploads or discord attachments
                local_videos: list[str] = []
                for v_url in video_candidates:
                    clean_v = v_url.lower().split("?")[0]
                    if any(clean_v.endswith(ext) for ext in video_extensions) or "discordapp." in v_url:
                        try:
                            saved_v = await MediaService.import_from_url(v_url, folder=f"discord/{target_channel_id}")
                            if saved_v:
                                local_videos.append(saved_v)
                        except Exception as err:
                            logger.warning(f"Failed to import video {v_url}: {err}")
                            local_videos.append(v_url)
                    else:
                        local_videos.append(v_url)

                # 4. Optional Translation (EN -> RU) & TL;DR block
                final_text = clean_text
                if auto_translate:
                    final_text = await translate_en_to_ru(clean_text)
                    final_text = generate_tldr_block(final_text)

                # Resolve all inline Discord images, emojis, and attachment URLs inside final_text to persistent storage
                try:
                    final_text = await MediaService.resolve_inline_media(final_text, folder=f"discord/{target_channel_id}")
                except Exception as res_err:
                    logger.warning(f"Error resolving inline media: {res_err}")

                # 5. Extract and clean Title
                import re as _re
                source_for_title = final_text if auto_translate else clean_text
                heading_match = _re.search(r'^#+\s+(.+)$', source_for_title, _re.MULTILINE)
                if custom_title:
                    raw_candidate = custom_title
                elif heading_match:
                    raw_candidate = heading_match.group(1).strip()
                else:
                    first_line = ""
                    for line in source_for_title.split("\n"):
                        cand = line.strip().lstrip("# ").strip()
                        if cand and len(cand) > 3:
                            first_line = cand
                            break
                    raw_candidate = first_line or f"Гайд от {author_tag}"

                title = clean_guide_title(raw_candidate, final_text, category_key)

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
                        video=local_videos,
                        views=0,
                    )
                    session.add(guide)
                else:
                    guide.title = title
                    guide.text = final_text
                    guide.category_key = category_key
                    if local_photos:
                        guide.photo = local_photos
                    if local_videos:
                        guide.video = local_videos

                # 7. Upsert into DiscordSyncedGuide tracker
                if not existing_synced:
                    synced_record = DiscordSyncedGuide(
                        discord_message_id=message_id,
                        discord_channel_id=target_channel_id,
                        guide_key=guide_key,
                        content_hash=content_hash,
                        author_tag=author_tag,
                    )
                    session.add(synced_record)
                else:
                    existing_synced.content_hash = content_hash
                    existing_synced.author_tag = author_tag

                await session.commit()
                logger.info(f"Successfully synced Discord guide '{guide_key}' from channel {target_channel_id}")

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

                return {"ok": True, "guide_key": guide_key}
        except Exception as e:
            logger.error(f"Error processing Discord message {message_id}: {e}", exc_info=True)
            return {"error": str(e)}

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

    @classmethod
    async def remove_synced_guide(cls, synced_id: int, delete_guide: bool = False) -> bool:
        async with get_sessionmaker()() as session:
            res = await session.execute(
                select(DiscordSyncedGuide).where(DiscordSyncedGuide.id == synced_id)
            )
            item = res.scalar_one_or_none()
            if not item:
                return False

            guide_key = item.guide_key
            await session.delete(item)

            if delete_guide and guide_key:
                guide_res = await session.execute(
                    select(Guide).where(Guide.key == guide_key)
                )
                guide = guide_res.scalar_one_or_none()
                if guide:
                    await session.delete(guide)

            await session.commit()
            return True

    @classmethod
    async def clear_synced_guides(cls, delete_guides: bool = False) -> int:
        async with get_sessionmaker()() as session:
            if delete_guides:
                res = await session.execute(select(DiscordSyncedGuide.guide_key))
                guide_keys = [k for k in res.scalars().all() if k]
                if guide_keys:
                    await session.execute(delete(Guide).where(Guide.key.in_(guide_keys)))

            result = await session.execute(delete(DiscordSyncedGuide))
            count = result.rowcount
            await session.commit()
            return count

    async def sanitize_all_existing_guides(self) -> dict:
        """
        Cleans titles, removes cat_init_* placeholders, and purges translation artifacts from all guides in DB.
        Uses direct atomic SQL queries to avoid ORM relationship issues.
        """
        import re
        from sqlalchemy import update
        from models.db_models import Guide
        updated = 0
        deleted_placeholders = 0
        async with get_sessionmaker()() as session:
            # 1. Delete cat_init_* placeholders directly
            del_res = await session.execute(
                delete(Guide).where(Guide.key.like("cat_init_%"))
            )
            deleted_placeholders = del_res.rowcount or 0

            # 2. Fetch all guides columns
            res = await session.execute(
                select(Guide.key, Guide.title, Guide.text, Guide.category_key)
            )
            rows = res.all()

            for key, title, text, category_key in rows:
                changed = False
                clean_t = clean_guide_title(title or "", text or "", category_key or "guide")

                if clean_t != (title or ""):
                    changed = True

                new_text = text or ""
                if text:
                    new_text = re.sub(r"__ГЛОСС\d+__", "", new_text)
                    new_text = re.sub(r"\baМаунт\b", "Количество", new_text, flags=re.IGNORECASE)
                    new_text = re.sub(r"\bСозвездиеs\b", "Созвездия", new_text, flags=re.IGNORECASE)
                    new_text = re.sub(r"\bПродвижениеs\b", "Продвижения", new_text, flags=re.IGNORECASE)
                    new_text = re.sub(r"\bЭтапs\b", "Этапы", new_text, flags=re.IGNORECASE)
                    if new_text != text:
                        changed = True

                if changed:
                    await session.execute(
                        update(Guide).where(Guide.key == key).values(
                            title=clean_t,
                            text=new_text
                        )
                    )
                    updated += 1

            await session.commit()

        from services.cache.redis_cache import cache_service
        await cache_service.invalidate_all()

        return {"updated_guides": updated, "deleted_placeholders": deleted_placeholders}


discord_sync_service = DiscordSyncService()
