import os
from inngest import Inngest

from core.config import settings

# Initialize Inngest client
# The ID should be unique to your application

# Prevent startup crash if signing key is missing (Anti-Pattern #18)
has_key = bool(os.getenv("INNGEST_SIGNING_KEY"))
is_prod = settings.ENVIRONMENT.lower() == "production" and has_key

inngest_client = Inngest(
    app_id="blackrose",
    is_production=is_prod,
    logger=None,
)
