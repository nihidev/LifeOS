"""Tests for the Small Wins API endpoints."""
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


async def _make_client(
    session: AsyncSession, user_id: UUID
) -> AsyncGenerator[AsyncClient, None]:
    """Build an AsyncClient with the given session and user_id overridden."""

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
# 1. POST returns 201
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_win_returns_201(client: AsyncClient) -> None:
    res = await client.post(
        "/api/v1/small-wins/", json={"date": _TODAY, "text": "First win"}
    )
    assert res.status_code == 201


# ---------------------------------------------------------------------------
# 2. Created win has correct text
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_win_text_stored(client: AsyncClient) -> None:
    res = await client.post(
        "/api/v1/small-wins/", json={"date": _TODAY, "text": "My win text"}
    )
    assert res.json()["text"] == "My win text"


# ---------------------------------------------------------------------------
# 3. GET by date returns list
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_wins_by_date_returns_list(client: AsyncClient) -> None:
    await client.post("/api/v1/small-wins/", json={"date": _TODAY, "text": "Win A"})
    await client.post("/api/v1/small-wins/", json={"date": _TODAY, "text": "Win B"})
    res = await client.get(f"/api/v1/small-wins/?date={_TODAY}")
    assert res.status_code == 200
    assert len(res.json()) == 2


# ---------------------------------------------------------------------------
# 4. GET by date with no wins returns empty list
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_wins_empty_date_returns_empty_list(client: AsyncClient) -> None:
    res = await client.get("/api/v1/small-wins/?date=2000-01-01")
    assert res.status_code == 200
    assert res.json() == []


# ---------------------------------------------------------------------------
# 5. PATCH updates text
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_update_win_changes_text(client: AsyncClient) -> None:
    create_res = await client.post(
        "/api/v1/small-wins/", json={"date": _TODAY, "text": "Original"}
    )
    win_id = create_res.json()["id"]
    patch_res = await client.patch(
        f"/api/v1/small-wins/{win_id}", json={"text": "Updated"}
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["text"] == "Updated"


# ---------------------------------------------------------------------------
# 6. PATCH non-existent returns 404
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_update_nonexistent_win_returns_404(client: AsyncClient) -> None:
    res = await client.patch(
        "/api/v1/small-wins/00000000-0000-0000-0000-000000000099",
        json={"text": "nope"},
    )
    assert res.status_code == 404


# ---------------------------------------------------------------------------
# 7. DELETE returns 200
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_delete_win_returns_200(client: AsyncClient) -> None:
    create_res = await client.post(
        "/api/v1/small-wins/", json={"date": _TODAY, "text": "To delete"}
    )
    win_id = create_res.json()["id"]
    del_res = await client.delete(f"/api/v1/small-wins/{win_id}")
    assert del_res.status_code == 200
    assert del_res.json() == {"message": "deleted"}


# ---------------------------------------------------------------------------
# 8. DELETE non-existent returns 404
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_delete_nonexistent_win_returns_404(client: AsyncClient) -> None:
    res = await client.delete(
        "/api/v1/small-wins/00000000-0000-0000-0000-000000000099"
    )
    assert res.status_code == 404


# ---------------------------------------------------------------------------
# 9. Empty text returns 422
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_with_empty_text_returns_422(client: AsyncClient) -> None:
    res = await client.post("/api/v1/small-wins/", json={"date": _TODAY, "text": ""})
    assert res.status_code == 422


# ---------------------------------------------------------------------------
# 10. Text over 500 chars returns 422
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_with_text_over_500_chars_returns_422(
    client: AsyncClient,
) -> None:
    res = await client.post(
        "/api/v1/small-wins/", json={"date": _TODAY, "text": "x" * 501}
    )
    assert res.status_code == 422


# ---------------------------------------------------------------------------
# 11. Cross-user GET isolation — user B sees empty list
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_cross_user_get_isolation(db_session: AsyncSession) -> None:
    async for client_a in _make_client(db_session, _USER_A):
        await client_a.post(
            "/api/v1/small-wins/", json={"date": _TODAY, "text": "User A win"}
        )

    async for client_b in _make_client(db_session, _USER_B):
        res = await client_b.get(f"/api/v1/small-wins/?date={_TODAY}")
        assert res.json() == []


# ---------------------------------------------------------------------------
# 12. Cross-user PATCH isolation — user B gets 404
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_cross_user_update_isolation(db_session: AsyncSession) -> None:
    win_id: str | None = None
    async for client_a in _make_client(db_session, _USER_A):
        res = await client_a.post(
            "/api/v1/small-wins/", json={"date": _TODAY, "text": "A's win"}
        )
        win_id = res.json()["id"]

    async for client_b in _make_client(db_session, _USER_B):
        res = await client_b.patch(
            f"/api/v1/small-wins/{win_id}", json={"text": "stolen"}
        )
        assert res.status_code == 404


# ---------------------------------------------------------------------------
# 13. Cross-user DELETE isolation — user B gets 404
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_cross_user_delete_isolation(db_session: AsyncSession) -> None:
    win_id: str | None = None
    async for client_a in _make_client(db_session, _USER_A):
        res = await client_a.post(
            "/api/v1/small-wins/", json={"date": _TODAY, "text": "A's win"}
        )
        win_id = res.json()["id"]

    async for client_b in _make_client(db_session, _USER_B):
        res = await client_b.delete(f"/api/v1/small-wins/{win_id}")
        assert res.status_code == 404


# ---------------------------------------------------------------------------
# 14. Unauthenticated request returns 403
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_unauthenticated_returns_403() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as raw_client:
        res = await raw_client.get(f"/api/v1/small-wins/?date={_TODAY}")
    assert res.status_code == 403


# ---------------------------------------------------------------------------
# 15. Create task — entry_type=task, response includes it
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_create_task_entry_type(client: AsyncClient) -> None:
    res = await client.post(
        "/api/v1/small-wins/",
        json={"date": _TODAY, "text": "Buy groceries", "entry_type": "task"},
    )
    assert res.status_code == 201
    body = res.json()
    assert body["entry_type"] == "task"
    assert body["completed"] is None


# ---------------------------------------------------------------------------
# 16. Toggle task completion via PATCH
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_toggle_task_completion(client: AsyncClient) -> None:
    create_res = await client.post(
        "/api/v1/small-wins/",
        json={"date": _TODAY, "text": "Clean up", "entry_type": "task"},
    )
    task_id = create_res.json()["id"]

    # Mark as complete
    patch_res = await client.patch(
        f"/api/v1/small-wins/{task_id}", json={"completed": True}
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["completed"] is True

    # Mark as incomplete
    patch_res2 = await client.patch(
        f"/api/v1/small-wins/{task_id}", json={"completed": False}
    )
    assert patch_res2.status_code == 200
    assert patch_res2.json()["completed"] is False


# ---------------------------------------------------------------------------
# 17. Stats — empty user returns total_wins=0 and all zero counts
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_stats_empty_user(client: AsyncClient) -> None:
    res = await client.get("/api/v1/small-wins/stats")
    assert res.status_code == 200
    body = res.json()
    assert body["total_wins"] == 0
    assert len(body["wins_last_7_days"]) == 7
    assert all(d["count"] == 0 for d in body["wins_last_7_days"])


# ---------------------------------------------------------------------------
# 18. Stats — 3 wins across different days gives total_wins=3
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_stats_total_wins_accumulates(client: AsyncClient) -> None:
    today = datetime.date.today()
    for offset in range(3):
        day = (today - datetime.timedelta(days=offset)).isoformat()
        await client.post("/api/v1/small-wins/", json={"date": day, "text": f"Win {offset}"})

    res = await client.get("/api/v1/small-wins/stats")
    assert res.status_code == 200
    assert res.json()["total_wins"] == 3


# ---------------------------------------------------------------------------
# 19. Stats — multiple wins same day all count towards total
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_stats_total_wins_same_day(client: AsyncClient) -> None:
    today = datetime.date.today().isoformat()
    for i in range(4):
        await client.post("/api/v1/small-wins/", json={"date": today, "text": f"Win {i}"})

    res = await client.get("/api/v1/small-wins/stats")
    assert res.status_code == 200
    assert res.json()["total_wins"] == 4


# ---------------------------------------------------------------------------
# 20. Stats — completed task counts towards total
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_stats_task_completed_counts(client: AsyncClient) -> None:
    today = datetime.date.today().isoformat()
    create_res = await client.post(
        "/api/v1/small-wins/",
        json={"date": today, "text": "Task", "entry_type": "task"},
    )
    task_id = create_res.json()["id"]
    await client.patch(f"/api/v1/small-wins/{task_id}", json={"completed": True})

    res = await client.get("/api/v1/small-wins/stats")
    assert res.status_code == 200
    body = res.json()
    assert body["total_wins"] == 1
    today_entry = body["wins_last_7_days"][-1]
    assert today_entry["count"] == 1


# ---------------------------------------------------------------------------
# 21. Stats — incomplete task does NOT count
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_stats_pending_task_not_counted(client: AsyncClient) -> None:
    today = datetime.date.today().isoformat()
    await client.post(
        "/api/v1/small-wins/",
        json={"date": today, "text": "Pending task", "entry_type": "task"},
    )
    res = await client.get("/api/v1/small-wins/stats")
    assert res.status_code == 200
    body = res.json()
    assert body["total_wins"] == 0
    today_entry = body["wins_last_7_days"][-1]
    assert today_entry["count"] == 0


# ---------------------------------------------------------------------------
# 22. Category stored and returned
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_category_stored_and_returned(client: AsyncClient) -> None:
    res = await client.post(
        "/api/v1/small-wins/",
        json={"date": _TODAY, "text": "Hit the gym", "category": "Health"},
    )
    assert res.status_code == 201
    body = res.json()
    assert body["category"] == "Health"

    # Verify it comes back in GET
    get_res = await client.get(f"/api/v1/small-wins/?date={_TODAY}")
    win = next(w for w in get_res.json() if w["id"] == body["id"])
    assert win["category"] == "Health"
