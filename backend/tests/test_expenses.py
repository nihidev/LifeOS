"""Tests for the Expenses API endpoints."""
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

_VALID = {
    "date": _TODAY,
    "amount": "12.50",
    "category": "Groceries",
    "note": "Supermarket",
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
# 1. POST returns 201
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_add_expense_returns_201(client: AsyncClient) -> None:
    res = await client.post("/api/v1/expenses/", json=_VALID)
    assert res.status_code == 201
    body = res.json()
    assert body["category"] == "Groceries"
    assert float(body["amount"]) == 12.50


# ---------------------------------------------------------------------------
# 2. Amount = 0 → 422
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_add_expense_zero_amount_422(client: AsyncClient) -> None:
    res = await client.post(
        "/api/v1/expenses/", json={**_VALID, "amount": "0"}
    )
    assert res.status_code == 422


# ---------------------------------------------------------------------------
# 3. Negative amount → 422
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_add_expense_negative_amount_422(client: AsyncClient) -> None:
    res = await client.post(
        "/api/v1/expenses/", json={**_VALID, "amount": "-5.00"}
    )
    assert res.status_code == 422


# ---------------------------------------------------------------------------
# 4. Invalid category → 422
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_add_expense_invalid_category_422(client: AsyncClient) -> None:
    res = await client.post(
        "/api/v1/expenses/", json={**_VALID, "category": "NotACategory"}
    )
    assert res.status_code == 422


# ---------------------------------------------------------------------------
# 5. GET by date returns list
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_expenses_by_date(client: AsyncClient) -> None:
    await client.post("/api/v1/expenses/", json=_VALID)
    res = await client.get(f"/api/v1/expenses/?date={_TODAY}")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert data[0]["category"] == "Groceries"


# ---------------------------------------------------------------------------
# 6. GET empty date → []
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_expenses_empty_date(client: AsyncClient) -> None:
    res = await client.get("/api/v1/expenses/?date=2000-01-01")
    assert res.status_code == 200
    assert res.json() == []


# ---------------------------------------------------------------------------
# 7. PATCH updates amount + category + note
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_patch_expense(client: AsyncClient) -> None:
    create_res = await client.post("/api/v1/expenses/", json=_VALID)
    expense_id = create_res.json()["id"]

    patch_res = await client.patch(
        f"/api/v1/expenses/{expense_id}",
        json={"amount": "99.99", "category": "Transport", "note": "Bus pass"},
    )
    assert patch_res.status_code == 200
    body = patch_res.json()
    assert float(body["amount"]) == 99.99
    assert body["category"] == "Transport"
    assert body["note"] == "Bus pass"


# ---------------------------------------------------------------------------
# 8. PATCH non-existent → 404
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_patch_nonexistent_expense_404(client: AsyncClient) -> None:
    res = await client.patch(
        "/api/v1/expenses/00000000-0000-0000-0000-000000000099",
        json={"amount": "5.00"},
    )
    assert res.status_code == 404


# ---------------------------------------------------------------------------
# 9. DELETE returns 200 and entry gone from GET
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_delete_expense(client: AsyncClient) -> None:
    create_res = await client.post("/api/v1/expenses/", json=_VALID)
    expense_id = create_res.json()["id"]

    del_res = await client.delete(f"/api/v1/expenses/{expense_id}")
    assert del_res.status_code == 200
    assert del_res.json() == {"message": "deleted"}

    get_res = await client.get(f"/api/v1/expenses/?date={_TODAY}")
    assert get_res.json() == []


# ---------------------------------------------------------------------------
# 10. DELETE non-existent → 404
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_delete_nonexistent_expense_404(client: AsyncClient) -> None:
    res = await client.delete(
        "/api/v1/expenses/00000000-0000-0000-0000-000000000099"
    )
    assert res.status_code == 404


# ---------------------------------------------------------------------------
# 11. Monthly summary: 2 entries same month → correct total + by_category
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_monthly_summary(client: AsyncClient) -> None:
    today = datetime.date.today()
    await client.post(
        "/api/v1/expenses/",
        json={"date": today.isoformat(), "amount": "20.00", "category": "Groceries"},
    )
    await client.post(
        "/api/v1/expenses/",
        json={"date": today.isoformat(), "amount": "10.50", "category": "Transport"},
    )

    res = await client.get(
        f"/api/v1/expenses/summary/monthly?year={today.year}&month={today.month}"
    )
    assert res.status_code == 200
    body = res.json()
    assert float(body["total"]) == 30.50
    categories = {item["category"] for item in body["by_category"]}
    assert "Groceries" in categories
    assert "Transport" in categories


# ---------------------------------------------------------------------------
# 12. Weekly summary: entry outside Mon–Sun window excluded
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_weekly_summary_excludes_outside_week(client: AsyncClient) -> None:
    today = datetime.date.today()
    # Entry inside the current week
    await client.post(
        "/api/v1/expenses/",
        json={"date": today.isoformat(), "amount": "15.00", "category": "Fitness"},
    )
    # Entry 14 days ago (definitely outside any current week)
    two_weeks_ago = (today - datetime.timedelta(days=14)).isoformat()
    await client.post(
        "/api/v1/expenses/",
        json={"date": two_weeks_ago, "amount": "100.00", "category": "Bills"},
    )

    res = await client.get(f"/api/v1/expenses/summary/weekly?date={today.isoformat()}")
    assert res.status_code == 200
    body = res.json()
    # Only the current-week entry counts
    assert float(body["total"]) == 15.00


# ---------------------------------------------------------------------------
# 13. Cross-user isolation — user B sees []
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_cross_user_isolation(db_session: AsyncSession) -> None:
    async for client_a in _make_client(db_session, _USER_A):
        await client_a.post("/api/v1/expenses/", json=_VALID)

    async for client_b in _make_client(db_session, _USER_B):
        res = await client_b.get(f"/api/v1/expenses/?date={_TODAY}")
        assert res.json() == []
