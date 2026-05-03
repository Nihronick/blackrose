from inngest import Inngest

# Initialize Inngest client
# The ID should be unique to your application
inngest_client = Inngest(
    app_id="blackrose",
    is_production=False, # Disable signature check for initial setup
    logger=None,
)
