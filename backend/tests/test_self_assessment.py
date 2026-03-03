"""Tests for the Self Assessment API endpoints."""
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
# 1. performed_well=true → score=100
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_performed_well_true_gives_score_100(client: AsyncClient) -> None:
    res = await client.post(
        "/api/v1/self-assessment/",
        json={"date": _TODAY, "performed_well_partner": True},
    )
    assert res.status_code == 200
    assert res.json()["integrity_score"] == 100
    assert res.json()["performed_well_partner"] is True


# ---------------------------------------------------------------------------
# 2. performed_well=false → score=0
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_performed_well_false_gives_score_0(client: AsyncClient) -> None:
    res = await client.post(
        "/api/v1/self-assessment/",
        json={"date": _TODAY, "performed_well_partner": False},
    )
    assert res.status_code == 200
    assert res.json()["integrity_score"] == 0
    assert res.json()["performed_well_partner"] is False


# ---------------------------------------------------------------------------
# 3. Note is stored
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_note_stored(client: AsyncClient) -> None:
    res = await client.post(
        "/api/v1/self-assessment/",
        json={"date": _TODAY, "performed_well_partner": True, "note": "Had a good day"},
    )
    assert res.json()["note"] == "Had a good day"


# ---------------------------------------------------------------------------
# 4. Second POST same day overwrites (UPSERT)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_upsert_same_day_overwrites(client: AsyncClient) -> None:
    await client.post(
        "/api/v1/self-assessment/",
        json={"date": _TODAY, "performed_well_partner": True, "note": "first"},
    )
    res = await client.post(
        "/api/v1/self-assessment/",
        json={"date": _TODAY, "performed_well_partner": False, "note": "updated"},
    )
    assert res.status_code == 200
    body = res.json()
    assert body["performed_well_partner"] is False
    assert body["integrity_score"] == 0
    assert body["note"] == "updated"


# ---------------------------------------------------------------------------
# 5. GET by date returns the entry
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_by_date(client: AsyncClient) -> None:
    await client.post(
        "/api/v1/self-assessment/",
        json={"date": _TODAY, "performed_well_partner": True},
    )
    res = await client.get(f"/api/v1/self-assessment/?date={_TODAY}")
    assert res.status_code == 200
    assert res.json()["integrity_score"] == 100


# ---------------------------------------------------------------------------
# 6. GET by date with no entry returns null
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_by_date_no_entry_returns_null(client: AsyncClient) -> None:
    res = await client.get("/api/v1/self-assessment/?date=2000-01-01")
    assert res.status_code == 200
    assert res.json() is None


# ---------------------------------------------------------------------------
# 7. History returns entries in descending date order
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_history_returns_entries(client: AsyncClient) -> None:
    await client.post(
        "/api/v1/self-assessment/",
        json={"date": _YESTERDAY, "performed_well_partner": True},
    )
    await client.post(
        "/api/v1/self-assessment/",
        json={"date": _TODAY, "performed_well_partner": False},
    )
    res = await client.get("/api/v1/self-assessment/history")
    assert res.status_code == 200
    body = res.json()
    assert len(body["entries"]) == 2
    # Descending — today first
    assert body["entries"][0]["date"] == _TODAY
    assert body["entries"][1]["date"] == _YESTERDAY


# ---------------------------------------------------------------------------
# 8. Average score calculated correctly
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_average_score(client: AsyncClient) -> None:
    await client.post(
        "/api/v1/self-assessment/",
        json={"date": _YESTERDAY, "performed_well_partner": True},
    )
    await client.post(
        "/api/v1/self-assessment/",
        json={"date": _TODAY, "performed_well_partner": False},
    )
    res = await client.get("/api/v1/self-assessment/history")
    # 100 + 0 = 100 avg 50.0
    assert res.json()["average_score"] == 50.0


# ---------------------------------------------------------------------------
# 9. History paginates with limit/offset
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_history_limit_offset(client: AsyncClient) -> None:
    await client.post(
        "/api/v1/self-assessment/",
        json={"date": _YESTERDAY, "performed_well_partner": True},
    )
    await client.post(
        "/api/v1/self-assessment/",
        json={"date": _TODAY, "performed_well_partner": False},
    )
    res = await client.get("/api/v1/self-assessment/history?limit=1&offset=0")
    assert len(res.json()["entries"]) == 1

    res2 = await client.get("/api/v1/self-assessment/history?limit=1&offset=1")
    assert len(res2.json()["entries"]) == 1

    # Different entries
    assert res.json()["entries"][0]["date"] != res2.json()["entries"][0]["date"]


# ---------------------------------------------------------------------------
# 10. History empty returns zero average
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_history_empty(client: AsyncClient) -> None:
    res = await client.get("/api/v1/self-assessment/history")
    assert res.status_code == 200
    assert res.json()["entries"] == []
    assert res.json()["average_score"] == 0.0


# ---------------------------------------------------------------------------
# 11. Cross-user isolation
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_cross_user_isolation(db_session: AsyncSession) -> None:
    async for client_a in _make_client(db_session, _USER_A):
        await client_a.post(
            "/api/v1/self-assessment/",
            json={"date": _TODAY, "performed_well_partner": True},
        )

    async for client_b in _make_client(db_session, _USER_B):
        res = await client_b.get(f"/api/v1/self-assessment/?date={_TODAY}")
        assert res.json() is None

        hist = await client_b.get("/api/v1/self-assessment/history")
        assert hist.json()["entries"] == []


# ---------------------------------------------------------------------------
# 12. Unauthenticated returns 403
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_unauthenticated_returns_403() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as raw_client:
        res = await raw_client.get(f"/api/v1/self-assessment/?date={_TODAY}")
    assert res.status_code == 403
