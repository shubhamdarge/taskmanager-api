import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_openapi_available():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        r = await ac.get("/openapi.json")
        assert r.status_code == 200
        assert "paths" in r.json()
