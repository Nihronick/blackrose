from core.config import settings
from core.logging import get_logger
from core.auth import hash_password
from core.db import get_sessionmaker
from models.db_models import LocalAdmin
from sqlalchemy.dialects.postgresql import insert

logger = get_logger("blackrose.services.setup")

async def seed_initial_admin():
    """Seeds initial admin users from environment variables."""
    # We need a method in member_service or a direct DB call to seed local admins
    # For now, let's assume we use member_service.upsert for Telegram admins
    # and we need a LocalAdminService for local logins.
    
    admins_to_seed = []
    
    if settings.INITIAL_ADMINS:
        for admin_str in settings.INITIAL_ADMINS.split(";"):
            if ":" in admin_str:
                admins_to_seed.append(admin_str.strip())
    
    if not admins_to_seed and settings.INITIAL_ADMIN and ":" in settings.INITIAL_ADMIN:
        admins_to_seed.append(settings.INITIAL_ADMIN.strip())
        
    if not admins_to_seed:
        return
    
    logger.info(f"Seeding {len(admins_to_seed)} local admin(s)...")
    
    async with get_sessionmaker()() as session:
        for admin_str in admins_to_seed:
            try:
                username, password = admin_str.split(":", 1)
                stmt = insert(LocalAdmin).values(
                    username=username,
                    password_hash=hash_password(password)
                ).on_conflict_do_update(
                    index_elements=[LocalAdmin.username],
                    set_={"password_hash": hash_password(password)}
                )
                await session.execute(stmt)
                logger.info(f"Local admin '{username}' seeded.")
            except Exception as e:
                logger.error(f"Failed to seed admin '{admin_str}': {e}")
        await session.commit()
