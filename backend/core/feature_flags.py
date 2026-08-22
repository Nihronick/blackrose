"""
Feature Flags — Simple Redis-backed feature toggle system.
Allows enabling/disabling features without redeployment.
"""
from core.logging import get_logger

logger = get_logger("blackrose.core.feature_flags")

# Default feature flags (used when Redis is unavailable or flag not set)
DEFAULT_FLAGS = {
    "build_planner": True,
    "tier_list": True,
    "guild_wars": False,
    "comments": True,
    "reactions": True,
    "favorites_sync": True,
    "search": True,
    "onboarding": True,
    "roadmap": True,
    "media_cache": True,
}

REDIS_KEY = "blackrose:feature_flags"


class FeatureFlagService:
    def __init__(self):
        self._local_cache: dict[str, bool] = dict(DEFAULT_FLAGS)
    
    async def get_all(self) -> dict[str, bool]:
        """Get all feature flags, falling back to defaults if Redis unavailable."""
        try:
            from services.cache.redis_cache import cache_service
            stored = await cache_service.get(REDIS_KEY)
            if stored and isinstance(stored, dict):
                merged = dict(DEFAULT_FLAGS)
                merged.update(stored)
                self._local_cache = merged
                return merged
        except Exception as e:
            logger.debug(f"Feature flags Redis read failed, using defaults: {e}")
        
        return dict(self._local_cache)
    
    async def get(self, flag_name: str) -> bool:
        """Get a single feature flag value."""
        flags = await self.get_all()
        return flags.get(flag_name, False)
    
    async def set_flag(self, flag_name: str, enabled: bool) -> dict[str, bool]:
        """Set a single feature flag."""
        flags = await self.get_all()
        flags[flag_name] = enabled
        
        try:
            from services.cache.redis_cache import cache_service
            await cache_service.set(REDIS_KEY, flags, expire=0)  # No expiry
        except Exception as e:
            logger.warning(f"Feature flags Redis write failed: {e}")
        
        self._local_cache = flags
        logger.info(f"Feature flag '{flag_name}' set to {enabled}")
        return flags
    
    async def set_all(self, flags: dict[str, bool]) -> dict[str, bool]:
        """Replace all feature flags."""
        merged = dict(DEFAULT_FLAGS)
        merged.update(flags)
        
        try:
            from services.cache.redis_cache import cache_service
            await cache_service.set(REDIS_KEY, merged, expire=0)
        except Exception as e:
            logger.warning(f"Feature flags Redis write failed: {e}")
        
        self._local_cache = merged
        logger.info(f"Feature flags bulk updated: {merged}")
        return merged


feature_flag_service = FeatureFlagService()
