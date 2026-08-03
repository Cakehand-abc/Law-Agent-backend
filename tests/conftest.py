import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.config import settings
from app.core.security import create_access_token

@pytest.fixture(scope="session")
def client():
    """
    Standard synchronous TestClient for testing HTTP endpoints.
    """
    with TestClient(app) as c:
        yield c

@pytest.fixture(scope="session")
async def async_client():
    """
    Asynchronous client for testing SSE (Streaming) or async-heavy flows.
    """
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as ac:
        yield ac

@pytest.fixture
def auth_headers():
    """
    Generates a valid developer JWT token and returns standard Authorization headers.
    """
    token = create_access_token(data={"sub": "12345"})
    return {"Authorization": f"Bearer {token}"}
