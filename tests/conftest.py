import pytest
from asgi_lifespan import LifespanManager
from httpx import AsyncClient

from app.main import create_app


@pytest.fixture
async def client():
    app = create_app()
    async with LifespanManager(app):
        async with AsyncClient(base_url="http://test") as ac:
            yield ac
