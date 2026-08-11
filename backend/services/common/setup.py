from core.config import settings
from core.logging import get_logger
from core.db import get_sessionmaker
from models.db_models import Member
from sqlalchemy.dialects.postgresql import insert

logger = get_logger("blackrose.services.setup")

async def seed_initial_admin():
    """Seeds initial Telegram Project Lead admin into Member database table."""
    logger.info("Initializing Telegram Project Lead admin seeding...")
    async with get_sessionmaker()() as session:
        try:
            # Seed main Founder ID (7215567457 / Nihronick)
            stmt = insert(Member).values(
                user_id=7215567457,
                username="Nihronick",
                first_name="Project Lead",
                role="project_admin"
            ).on_conflict_do_update(
                index_elements=[Member.user_id],
                set_={"role": "project_admin", "username": "Nihronick"}
            )
            await session.execute(stmt)
            await session.commit()
            logger.info("Project Lead Telegram admin seeded with 'project_admin' role.")
        except Exception as e:
            logger.error(f"Failed to seed Project Lead admin: {e}")
