from inngest import Inngest

from core.config import settings

# Initialize Inngest client
# The ID should be unique to your application
is_prod = settings.ENVIRONMENT.lower() == "production"

inngest_client = Inngest(
    app_id="blackrose",
    is_production=is_prod,
    logger=None,
)
