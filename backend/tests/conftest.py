import os
import sys
import pytest
from unittest.mock import AsyncMock, MagicMock

# Add backend to path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

@pytest.fixture(autouse=True)
def mock_env():
    """Ensure environment variables are set for tests."""
    os.environ["BOT_TOKEN"] = "123456789:AAFakeTokenForTesting"
    os.environ["DATABASE_URL"] = "postgresql+asyncpg://user:pass@localhost/test"
    os.environ["HF_TOKEN"] = "hf_test_token"
    os.environ["HF_DATASET_REPO"] = "test/dataset"
    os.environ["GEMINI_API_KEY"] = "gemini_test_key"
    yield

@pytest.fixture
def mock_db():
    """Mock database session."""
    session = AsyncMock()
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.close = AsyncMock()

    # Mock context manager
    session_cm = MagicMock()
    session_cm.__aenter__ = AsyncMock(return_value=session)
    session_cm.__aexit__ = AsyncMock()

    return session
