"""Tests for the Food Log API endpoints."""
import datetime
from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock, patch
from uuid import UUID

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from app.core.database import Base, get_db
from app.core.deps import get_current_user
from app.main import app

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_TEST_DB_URL = "sqlite+aiosqlite:///:memory:"
_USER_A = UUID("00000000-0000-0000-0000-000000000001")
_USER_B = UUID("00000000-0000-0000-0000-000000000002")
_TODAY = datetime.date.today().isoformat()

_VALID_LOG = {
    "date": _TODAY,
    "consumed_at": "08:30",
    "food_item": "Oatmeal with berries",
}


async def _make_client(
    session: AsyncSession, user_id: UUID
) -> AsyncGenerator[AsyncClient, None]:
    async def _override_db() -> AsyncGenerator[AsyncSession, None]:
        yield session

    def _override_user() -> UUID:
        return user_id

    app.dependency_overrides[get_db] = _override_db
    app.dependency_overrides[get_current_user] = _override_user

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client

    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    engine = create_async_engine(_TEST_DB_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    session = AsyncSession(engine)
    try:
        yield session
    finally:
        await session.close()
        await engine.dispose()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async for c in _make_client(db_session, _USER_A):
        yield c


# ---------------------------------------------------------------------------
# 1. POST creates log entry → 201, returns ai_comment (str or null)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_food_log_201(client: AsyncClient) -> None:
    with patch(
        "app.services.food_log_service._get_ai_comment",
        new=AsyncMock(return_value="A great source of slow-release energy."),
    ):
        res = await client.post("/api/v1/food-logs/", json=_VALID_LOG)
    assert res.status_code == 201
    body = res.json()
    assert body["food_item"] == "Oatmeal with berries"
    assert body["consumed_at"] == "08:30"
    assert body["ai_comment"] == "A great source of slow-release energy."


@pytest.mark.asyncio
async def test_create_food_log_no_openai_key(client: AsyncClient) -> None:
    """When no API key → ai_comment is null."""
    with patch(
        "app.services.food_log_service._get_ai_comment",
        new=AsyncMock(return_value=None),
    ):
        res = await client.post("/api/v1/food-logs/", json=_VALID_LOG)
    assert res.status_code == 201
    assert res.json()["ai_comment"] is None


# ---------------------------------------------------------------------------
# 2. Invalid time format → 422
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_invalid_time_format_422(client: AsyncClient) -> None:
    res = await client.post(
        "/api/v1/food-logs/", json={**_VALID_LOG, "consumed_at": "8:30am"}
    )
    assert res.status_code == 422


# ---------------------------------------------------------------------------
# 3. GET by date returns entries ordered by consumed_at
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_logs_by_date(client: AsyncClient) -> None:
    with patch(
        "app.services.food_log_service._get_ai_comment",
        new=AsyncMock(return_value=None),
    ):
        await client.post("/api/v1/food-logs/", json={**_VALID_LOG, "consumed_at": "12:00"})
        await client.post("/api/v1/food-logs/", json={**_VALID_LOG, "consumed_at": "07:00"})

    res = await client.get(f"/api/v1/food-logs/?date={_TODAY}")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 2
    assert data[0]["consumed_at"] == "07:00"
    assert data[1]["consumed_at"] == "12:00"


# ---------------------------------------------------------------------------
# 4. GET wrong date → []
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_logs_empty_date(client: AsyncClient) -> None:
    res = await client.get("/api/v1/food-logs/?date=2000-01-01")
    assert res.status_code == 200
    assert res.json() == []


# ---------------------------------------------------------------------------
# 5. DELETE → 200, entry gone from GET
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_delete_food_log(client: AsyncClient) -> None:
    with patch(
        "app.services.food_log_service._get_ai_comment",
        new=AsyncMock(return_value=None),
    ):
        create_res = await client.post("/api/v1/food-logs/", json=_VALID_LOG)
    entry_id = create_res.json()["id"]

    del_res = await client.delete(f"/api/v1/food-logs/{entry_id}")
    assert del_res.status_code == 200
    assert del_res.json() == {"message": "deleted"}

    get_res = await client.get(f"/api/v1/food-logs/?date={_TODAY}")
    assert get_res.json() == []


@pytest.mark.asyncio
async def test_delete_nonexistent_404(client: AsyncClient) -> None:
    res = await client.delete(
        "/api/v1/food-logs/00000000-0000-0000-0000-000000000099"
    )
    assert res.status_code == 404


# ---------------------------------------------------------------------------
# 6. Water counter: get → 0 when no record
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_water_get_default_zero(client: AsyncClient) -> None:
    res = await client.get(f"/api/v1/food-logs/water?date={_TODAY}")
    assert res.status_code == 200
    assert res.json()["glasses"] == 0


# ---------------------------------------------------------------------------
# 7. Water increment → glasses increases
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_water_increment(client: AsyncClient) -> None:
    res1 = await client.post(
        "/api/v1/food-logs/water/increment", json={"date": _TODAY}
    )
    assert res1.status_code == 200
    assert res1.json()["glasses"] == 1

    res2 = await client.post(
        "/api/v1/food-logs/water/increment", json={"date": _TODAY}
    )
    assert res2.json()["glasses"] == 2


# ---------------------------------------------------------------------------
# 8. Water decrement → floors at 0
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_water_decrement(client: AsyncClient) -> None:
    # Increment to 1 first
    await client.post("/api/v1/food-logs/water/increment", json={"date": _TODAY})

    res = await client.post(
        "/api/v1/food-logs/water/decrement", json={"date": _TODAY}
    )
    assert res.status_code == 200
    assert res.json()["glasses"] == 0

    # Decrement again — stays at 0
    res2 = await client.post(
        "/api/v1/food-logs/water/decrement", json={"date": _TODAY}
    )
    assert res2.json()["glasses"] == 0


# ---------------------------------------------------------------------------
# 9. Cross-user isolation
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_cross_user_isolation(db_session: AsyncSession) -> None:
    async for client_a in _make_client(db_session, _USER_A):
        with patch(
            "app.services.food_log_service._get_ai_comment",
            new=AsyncMock(return_value=None),
        ):
            await client_a.post("/api/v1/food-logs/", json=_VALID_LOG)
        await client_a.post(
            "/api/v1/food-logs/water/increment", json={"date": _TODAY}
        )

    async for client_b in _make_client(db_session, _USER_B):
        logs_res = await client_b.get(f"/api/v1/food-logs/?date={_TODAY}")
        assert logs_res.json() == []

        water_res = await client_b.get(f"/api/v1/food-logs/water?date={_TODAY}")
        assert water_res.json()["glasses"] == 0
