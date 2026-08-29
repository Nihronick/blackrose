from core.logging import get_logger
from core.db import get_sessionmaker
from models.db_models import Member
from sqlalchemy.dialects.postgresql import insert
from core.config import settings

logger = get_logger("blackrose.services.setup")

async def seed_initial_admin():
    """Seeds initial Telegram Project Lead admin into Member database table."""
    logger.info("Initializing Telegram Project Lead admin seeding...")
    async with get_sessionmaker()() as session:
        try:
            admin_id_str = settings.ADMIN_USERS.split(",")[0].strip() if settings.ADMIN_USERS else ""
            if not admin_id_str.isdigit():
                logger.info("No initial admin users configured in ADMIN_USERS.")
                return
            admin_id = int(admin_id_str)
            stmt = insert(Member).values(
                user_id=admin_id,
                username="Admin",
                first_name="Project Lead",
                role="project_admin"
            ).on_conflict_do_update(
                index_elements=[Member.user_id],
                set_={"role": "project_admin", "username": "Admin"}
            )
            await session.execute(stmt)
            await session.commit()
            logger.info("Project Lead Telegram admin seeded with 'project_admin' role.")
        except Exception as e:
            logger.error(f"Failed to seed Project Lead admin: {e}")
