import inngest
from core.inngest_client import inngest_client

@inngest_client.create_function(
    fn_id="test_job",
    trigger=inngest.TriggerEvent(event="app/test.job"),
)
async def test_job(ctx: inngest.Context, step: inngest.Step):
    """
    Simple test job to verify Inngest execution on Hugging Face.
    """
    return {"message": "Success from BlackRose Background Job!"}
