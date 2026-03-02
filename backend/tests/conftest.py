from collections.abc import AsyncGenerator
from uuid import UUID

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app.core.database import Base, get_db
from app.core.deps import get_current_user
from app.main import app

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_TEST_DB_URL = "sqlite+aiosqlite:///:memory:"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture(scope="function")
async def test_db() -> AsyncGenerator[AsyncSession, None]:
    """In-memory SQLite database for each test function."""
    engine = create_async_engine(_TEST_DB_URL, echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session = AsyncSession(engine)
    try:
        yield session
    finally:
        await session.close()
        await engine.dispose()


@pytest.fixture(scope="function")
def mock_user_id() -> UUID:
    """Stable mock UUID representing the test user."""
    return UUID("00000000-0000-0000-0000-000000000001")


@pytest_asyncio.fixture(scope="function")
async def async_client(
    test_db: AsyncSession,
    mock_user_id: UUID,
) -> AsyncGenerator[AsyncClient, None]:
    """HTTP test client with DB and auth dependencies overridden."""

    async def _override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield test_db

    def _override_get_current_user() -> UUID:
        return mock_user_id

    app.dependency_overrides[get_db] = _override_get_db
    app.dependency_overrides[get_current_user] = _override_get_current_user

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client

    app.dependency_overrides.clear()
