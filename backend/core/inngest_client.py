from inngest import Inngest
from core.config import settings

# Initialize Inngest client
# The ID should be unique to your application
inngest_client = Inngest(
    app_id="blackrose",
    logger=None, # It will use the default logger
)
