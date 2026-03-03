"""Tests for the Workouts API endpoints."""
import datetime
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
# Helpers
# ---------------------------------------------------------------------------

_TEST_DB_URL = "sqlite+aiosqlite:///:memory:"
_USER_A = UUID("00000000-0000-0000-0000-000000000001")
_USER_B = UUID("00000000-0000-0000-0000-000000000002")
_TODAY = datetime.date.today().isoformat()
_YESTERDAY = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
_TWO_AGO = (datetime.date.today() - datetime.timedelta(days=2)).isoformat()


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
# 1. POST creates a workout (200)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_log_workout_returns_200(client: AsyncClient) -> None:
    res = await client.post(
        "/api/v1/workouts/", json={"date": _TODAY, "did_workout": True}
    )
    assert res.status_code == 200


# ---------------------------------------------------------------------------
# 2. POST stores the correct fields
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_log_workout_fields_stored(client: AsyncClient) -> None:
    res = await client.post(
        "/api/v1/workouts/",
        json={
            "date": _TODAY,
            "did_workout": True,
            "activity_type": "Running",
            "duration_mins": 30,
            "notes": "Felt great",
        },
    )
    body = res.json()
    assert body["did_workout"] is True
    assert body["activity_type"] == "Running"
    assert body["duration_mins"] == 30
    assert body["notes"] == "Felt great"


# ---------------------------------------------------------------------------
# 3. POST upsert — same date replaces existing
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_upsert_same_date_replaces(client: AsyncClient) -> None:
    await client.post(
        "/api/v1/workouts/", json={"date": _TODAY, "did_workout": True, "notes": "first"}
    )
    res = await client.post(
        "/api/v1/workouts/", json={"date": _TODAY, "did_workout": False, "notes": "second"}
    )
    assert res.status_code == 200
    body = res.json()
    assert body["did_workout"] is False
    assert body["notes"] == "second"


# ---------------------------------------------------------------------------
# 4. GET by date returns the entry
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_workout_by_date(client: AsyncClient) -> None:
    await client.post(
        "/api/v1/workouts/", json={"date": _TODAY, "did_workout": True}
    )
    res = await client.get(f"/api/v1/workouts/?date={_TODAY}")
    assert res.status_code == 200
    assert res.json()["did_workout"] is True


# ---------------------------------------------------------------------------
# 5. GET by date with no entry returns null
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_workout_no_entry_returns_null(client: AsyncClient) -> None:
    res = await client.get("/api/v1/workouts/?date=2000-01-01")
    assert res.status_code == 200
    assert res.json() is None


# ---------------------------------------------------------------------------
# 6. Streak: 0 when no entries
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_streak_zero_with_no_entries(client: AsyncClient) -> None:
    res = await client.get("/api/v1/workouts/streak")
    assert res.status_code == 200
    assert res.json()["current_streak"] == 0
    assert res.json()["longest_streak"] == 0


# ---------------------------------------------------------------------------
# 7. Streak counts consecutive workout days from today
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_streak_counts_consecutive_days(client: AsyncClient) -> None:
    for d in [_TODAY, _YESTERDAY, _TWO_AGO]:
        await client.post("/api/v1/workouts/", json={"date": d, "did_workout": True})
    res = await client.get("/api/v1/workouts/streak")
    assert res.json()["current_streak"] == 3


# ---------------------------------------------------------------------------
# 8. Streak resets on rest day
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_streak_resets_on_rest_day(client: AsyncClient) -> None:
    await client.post(
        "/api/v1/workouts/", json={"date": _TODAY, "did_workout": True}
    )
    await client.post(
        "/api/v1/workouts/", json={"date": _YESTERDAY, "did_workout": False}
    )
    res = await client.get("/api/v1/workouts/streak")
    assert res.json()["current_streak"] == 1


# ---------------------------------------------------------------------------
# 9. Streak resets on missing day
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_streak_resets_on_missing_day(client: AsyncClient) -> None:
    # today worked out, yesterday has no entry → streak = 1
    await client.post(
        "/api/v1/workouts/", json={"date": _TODAY, "did_workout": True}
    )
    res = await client.get("/api/v1/workouts/streak")
    assert res.json()["current_streak"] == 1


# ---------------------------------------------------------------------------
# 10. Longest streak tracked correctly
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_longest_streak(client: AsyncClient) -> None:
    # 3-day streak, then rest, then 1 day
    three_ago = (datetime.date.today() - datetime.timedelta(days=3)).isoformat()
    for d in [_TWO_AGO, _YESTERDAY, three_ago]:
        await client.post("/api/v1/workouts/", json={"date": d, "did_workout": True})
    await client.post(
        "/api/v1/workouts/", json={"date": _TODAY, "did_workout": False}
    )
    res = await client.get("/api/v1/workouts/streak")
    assert res.json()["longest_streak"] == 3
    assert res.json()["current_streak"] == 0


# ---------------------------------------------------------------------------
# 11. Monthly summary returns correct counts
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_monthly_summary(client: AsyncClient) -> None:
    today = datetime.date.today()
    await client.post(
        "/api/v1/workouts/",
        json={"date": today.isoformat(), "did_workout": True},
    )
    res = await client.get(
        f"/api/v1/workouts/monthly-summary?year={today.year}&month={today.month}"
    )
    assert res.status_code == 200
    body = res.json()
    assert body["workout_days"] == 1
    assert body["rest_days"] == 0
    assert body["total_days"] > 0


# ---------------------------------------------------------------------------
# 12. Cross-user isolation — user B sees no data
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_cross_user_isolation(db_session: AsyncSession) -> None:
    async for client_a in _make_client(db_session, _USER_A):
        await client_a.post(
            "/api/v1/workouts/", json={"date": _TODAY, "did_workout": True}
        )

    async for client_b in _make_client(db_session, _USER_B):
        res = await client_b.get(f"/api/v1/workouts/?date={_TODAY}")
        assert res.json() is None


# ---------------------------------------------------------------------------
# 13. Unauthenticated returns 403
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_unauthenticated_returns_403() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as raw_client:
        res = await raw_client.get(f"/api/v1/workouts/?date={_TODAY}")
    assert res.status_code == 403
