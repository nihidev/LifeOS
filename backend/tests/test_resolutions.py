"""Tests for the Resolutions API endpoints."""
import datetime
from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock, patch
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

_VALID = {"title": "Run a marathon", "description": "Complete 42km race"}


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
# 1. POST returns 201, defaults: status=not_started, progress=0
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_resolution_returns_201(client: AsyncClient) -> None:
    res = await client.post("/api/v1/resolutions/", json=_VALID)
    assert res.status_code == 201
    body = res.json()
    assert body["title"] == "Run a marathon"
    assert body["status"] == "not_started"
    assert body["progress_percent"] == 0
    assert body["check_ins"] == []


# ---------------------------------------------------------------------------
# 2. progress_percent > 100 → 422
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_update_progress_over_100_422(client: AsyncClient) -> None:
    create_res = await client.post("/api/v1/resolutions/", json=_VALID)
    rid = create_res.json()["id"]
    res = await client.patch(f"/api/v1/resolutions/{rid}", json={"progress_percent": 101})
    assert res.status_code == 422


# ---------------------------------------------------------------------------
# 3. progress_percent < 0 → 422
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_update_progress_negative_422(client: AsyncClient) -> None:
    create_res = await client.post("/api/v1/resolutions/", json=_VALID)
    rid = create_res.json()["id"]
    res = await client.patch(f"/api/v1/resolutions/{rid}", json={"progress_percent": -1})
    assert res.status_code == 422


# ---------------------------------------------------------------------------
# 4. PATCH status=completed auto-sets progress_percent=100
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_complete_status_sets_progress_100(client: AsyncClient) -> None:
    create_res = await client.post("/api/v1/resolutions/", json=_VALID)
    rid = create_res.json()["id"]

    patch_res = await client.patch(
        f"/api/v1/resolutions/{rid}", json={"status": "completed"}
    )
    assert patch_res.status_code == 200
    body = patch_res.json()
    assert body["status"] == "completed"
    assert body["progress_percent"] == 100


# ---------------------------------------------------------------------------
# 5. GET ?status_filter=in_progress filters correctly
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_list_filter_by_status(client: AsyncClient) -> None:
    # Create two resolutions
    r1 = await client.post("/api/v1/resolutions/", json={"title": "Goal A"})
    r2 = await client.post("/api/v1/resolutions/", json={"title": "Goal B"})
    rid1 = r1.json()["id"]

    # Advance one to in_progress
    await client.patch(f"/api/v1/resolutions/{rid1}", json={"status": "in_progress"})

    # Filter by in_progress
    res = await client.get("/api/v1/resolutions/?status_filter=in_progress")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 1
    assert data[0]["id"] == rid1


# ---------------------------------------------------------------------------
# 6. Check-in upsert: POST same (year, month) twice → only one row, rating updated
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_checkin_upsert(client: AsyncClient) -> None:
    create_res = await client.post("/api/v1/resolutions/", json=_VALID)
    rid = create_res.json()["id"]

    checkin = {"year": 2026, "month": 3, "rating": 2, "note": "Slow start"}
    await client.post(f"/api/v1/resolutions/{rid}/check-ins", json=checkin)

    # Second POST same year/month — updates rating
    updated_checkin = {"year": 2026, "month": 3, "rating": 4, "note": "Better now"}
    res2 = await client.post(f"/api/v1/resolutions/{rid}/check-ins", json=updated_checkin)
    assert res2.status_code == 200
    assert res2.json()["rating"] == 4

    # Verify only one check-in exists on the resolution
    get_res = await client.get("/api/v1/resolutions/")
    resolution = next(r for r in get_res.json() if r["id"] == rid)
    assert len(resolution["check_ins"]) == 1
    assert resolution["check_ins"][0]["rating"] == 4


# ---------------------------------------------------------------------------
# 7. First check-in auto-advances not_started → in_progress
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_first_checkin_advances_status(client: AsyncClient) -> None:
    create_res = await client.post("/api/v1/resolutions/", json=_VALID)
    rid = create_res.json()["id"]
    assert create_res.json()["status"] == "not_started"

    await client.post(
        f"/api/v1/resolutions/{rid}/check-ins",
        json={"year": 2026, "month": 1, "rating": 3},
    )

    get_res = await client.get("/api/v1/resolutions/")
    resolution = next(r for r in get_res.json() if r["id"] == rid)
    assert resolution["status"] == "in_progress"


# ---------------------------------------------------------------------------
# 8. PATCH non-existent id → 404
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_patch_nonexistent_404(client: AsyncClient) -> None:
    res = await client.patch(
        "/api/v1/resolutions/00000000-0000-0000-0000-000000000099",
        json={"title": "Ghost"},
    )
    assert res.status_code == 404


# ---------------------------------------------------------------------------
# 9. Cross-user isolation — user B sees []
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_cross_user_isolation(db_session: AsyncSession) -> None:
    async for client_a in _make_client(db_session, _USER_A):
        await client_a.post("/api/v1/resolutions/", json=_VALID)

    async for client_b in _make_client(db_session, _USER_B):
        res = await client_b.get("/api/v1/resolutions/")
        assert res.json() == []


# ---------------------------------------------------------------------------
# 10. DELETE own resolution → 204, gone from list
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_delete_resolution(client: AsyncClient) -> None:
    create_res = await client.post("/api/v1/resolutions/", json=_VALID)
    rid = create_res.json()["id"]

    del_res = await client.delete(f"/api/v1/resolutions/{rid}")
    assert del_res.status_code == 204

    list_res = await client.get("/api/v1/resolutions/")
    assert all(r["id"] != rid for r in list_res.json())


# ---------------------------------------------------------------------------
# 11. DELETE other user's resolution → 404
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_delete_other_user_resolution_404(db_session: AsyncSession) -> None:
    async for client_a in _make_client(db_session, _USER_A):
        create_res = await client_a.post("/api/v1/resolutions/", json=_VALID)
        rid = create_res.json()["id"]

    async for client_b in _make_client(db_session, _USER_B):
        res = await client_b.delete(f"/api/v1/resolutions/{rid}")
        assert res.status_code == 404


# ---------------------------------------------------------------------------
# 12. GET /analysis returns valid structure (monkeypatched OpenAI)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_analysis_returns_structure(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    # Create a resolution first
    create_res = await client.post("/api/v1/resolutions/", json=_VALID)
    rid = create_res.json()["id"]

    fake_analyses = [
        {
            "resolution_id": rid,
            "resolution_title": "Run a marathon",
            "signal": "no_signal",
            "evidence": [],
            "suggestion": "Keep logging wins!",
        }
    ]
    import json

    mock_message = MagicMock()
    mock_message.choices = [MagicMock()]
    mock_message.choices[0].message.content = json.dumps(fake_analyses)

    mock_client = AsyncMock()
    mock_client.chat = MagicMock()
    mock_client.chat.completions = MagicMock()
    mock_client.chat.completions.create = AsyncMock(return_value=mock_message)

    with (
        patch("app.services.resolution_service.settings") as mock_settings,
        patch("app.services.resolution_service.AsyncOpenAI", return_value=mock_client),
    ):
        mock_settings.OPENAI_API_KEY = "sk-test"
        res = await client.get("/api/v1/resolutions/analysis")

    assert res.status_code == 200
    body = res.json()
    assert "generated_at" in body
    assert "analyses" in body
    assert isinstance(body["analyses"], list)
    assert len(body["analyses"]) == 1
    assert body["analyses"][0]["signal"] in ("on_track", "at_risk", "no_signal")
