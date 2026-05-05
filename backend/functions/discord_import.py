import inngest
from core.inngest_client import inngest_client
from services.discord_lab.lab_synthesizer import discord_lab_service
from services.guides.service import guide_service
from services.common.media import media_service
from services.common.utils import normalize_icon_syntax
from core.logging import get_logger

logger = get_logger("blackrose.functions.discord")

@inngest_client.create_function(
    fn_id="discord-import-guide",
    trigger=inngest.TriggerEvent(event="discord/guide.import"),
)
async def discord_import_guide(ctx: inngest.Context):
    """
    Orchestrates the full guide import process from Discord messages.
    """
    messages = ctx.event.data.get("messages", [])
    category_key = ctx.event.data.get("category_key", "imported")
    guide_key = ctx.event.data.get("guide_key")

    if not messages:
        return {"status": "skipped", "reason": "no_messages"}

    # Step 1: AI Synthesis (Gemini)
    # We use step.run so that if it succeeds, it's never called again even if later steps fail.
    synthesis = await ctx.step.run(
        "ai-synthesis",
        lambda: discord_lab_service.synthesize_ai(messages)
    )

    content = synthesis["content"]
    raw_media = synthesis["media"]

    # Step 2: Media Processing (HF Uploads)
    processed_media = []
    if raw_media:
        # Limit to 10 media items to prevent unbounded processing
        limited_media = raw_media[:10]
        processed_media = await ctx.step.run(
            "process-media",
            lambda: _process_all_media(limited_media)
        )

    # Step 3: Final Upsert to Database
    # We generate a key if not provided
    if not guide_key:
        import uuid
        guide_key = f"imported-{str(uuid.uuid4())[:8]}"

    await ctx.step.run(
        "save-to-db",
        lambda: guide_service.upsert(
            key=guide_key,
            data={
                "category_key": category_key,
                "title": ctx.event.data.get("title", "Imported Guide"),
                "text": normalize_icon_syntax(content),
                "photo": [m for m in processed_media if m.endswith(('.webp', '.png', '.jpg'))],
                "video": [m for m in processed_media if m.endswith(('.mp4', '.mov'))],
                "sort_order": 0
            }
        )
    )

    return {"status": "success", "guide_key": guide_key}

async def _process_all_media(urls: list[str]) -> list[str]:
    results = []
    for url in urls:
        try:
            # Re-using our existing media service
            new_url = await media_service.import_from_url(url, folder="imported")
            results.append(new_url)
        except Exception as e:
            logger.error(f"Media import failed for {url}: {e}")
    return results
