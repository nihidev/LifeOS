"""Tests for the Grocery List API endpoints."""
from collections.abc import AsyncGenerator
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

_VALID_ITEM = {"item": "Oat milk", "quantity": "2 litres"}


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
# 1. POST → 201
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_add_item_201(client: AsyncClient) -> None:
    res = await client.post("/api/v1/grocery/", json=_VALID_ITEM)
    assert res.status_code == 201
    body = res.json()
    assert body["item"] == "Oat milk"
    assert body["quantity"] == "2 litres"
    assert body["checked"] is False


@pytest.mark.asyncio
async def test_add_item_without_quantity(client: AsyncClient) -> None:
    res = await client.post("/api/v1/grocery/", json={"item": "Bananas"})
    assert res.status_code == 201
    assert res.json()["quantity"] is None


# ---------------------------------------------------------------------------
# 2. GET all → unchecked first
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_all_unchecked_first(client: AsyncClient) -> None:
    r1 = await client.post("/api/v1/grocery/", json={"item": "Milk"})
    r2 = await client.post("/api/v1/grocery/", json={"item": "Eggs"})
    item1_id = r1.json()["id"]
    # Check item1
    await client.patch(f"/api/v1/grocery/{item1_id}", json={"checked": True})

    res = await client.get("/api/v1/grocery/")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 2
    # Unchecked (Eggs) should come first
    assert data[0]["checked"] is False
    assert data[1]["checked"] is True


# ---------------------------------------------------------------------------
# 3. PATCH checked=true
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_patch_checked(client: AsyncClient) -> None:
    create_res = await client.post("/api/v1/grocery/", json=_VALID_ITEM)
    item_id = create_res.json()["id"]

    patch_res = await client.patch(
        f"/api/v1/grocery/{item_id}", json={"checked": True}
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["checked"] is True


# ---------------------------------------------------------------------------
# 4. PATCH item text
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_patch_item_text(client: AsyncClient) -> None:
    create_res = await client.post("/api/v1/grocery/", json=_VALID_ITEM)
    item_id = create_res.json()["id"]

    patch_res = await client.patch(
        f"/api/v1/grocery/{item_id}", json={"item": "Almond milk", "quantity": "1 litre"}
    )
    assert patch_res.status_code == 200
    body = patch_res.json()
    assert body["item"] == "Almond milk"
    assert body["quantity"] == "1 litre"


# ---------------------------------------------------------------------------
# 5. PATCH non-existent → 404
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_patch_nonexistent_404(client: AsyncClient) -> None:
    res = await client.patch(
        "/api/v1/grocery/00000000-0000-0000-0000-000000000099",
        json={"checked": True},
    )
    assert res.status_code == 404


# ---------------------------------------------------------------------------
# 6. DELETE → 200, gone from list
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_delete_item(client: AsyncClient) -> None:
    create_res = await client.post("/api/v1/grocery/", json=_VALID_ITEM)
    item_id = create_res.json()["id"]

    del_res = await client.delete(f"/api/v1/grocery/{item_id}")
    assert del_res.status_code == 200
    assert del_res.json() == {"message": "deleted"}

    get_res = await client.get("/api/v1/grocery/")
    assert get_res.json() == []


@pytest.mark.asyncio
async def test_delete_nonexistent_404(client: AsyncClient) -> None:
    res = await client.delete(
        "/api/v1/grocery/00000000-0000-0000-0000-000000000099"
    )
    assert res.status_code == 404


# ---------------------------------------------------------------------------
# 7. clear-checked → returns deleted_count, checked items gone
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_clear_checked(client: AsyncClient) -> None:
    r1 = await client.post("/api/v1/grocery/", json={"item": "Bread"})
    r2 = await client.post("/api/v1/grocery/", json={"item": "Butter"})
    r3 = await client.post("/api/v1/grocery/", json={"item": "Cheese"})

    # Check 2 items
    await client.patch(f"/api/v1/grocery/{r1.json()['id']}", json={"checked": True})
    await client.patch(f"/api/v1/grocery/{r2.json()['id']}", json={"checked": True})

    clear_res = await client.post("/api/v1/grocery/clear-checked")
    assert clear_res.status_code == 200
    assert clear_res.json()["deleted_count"] == 2

    remaining = await client.get("/api/v1/grocery/")
    data = remaining.json()
    assert len(data) == 1
    assert data[0]["item"] == "Cheese"
    assert data[0]["checked"] is False


@pytest.mark.asyncio
async def test_clear_checked_none_checked(client: AsyncClient) -> None:
    await client.post("/api/v1/grocery/", json={"item": "Bread"})
    res = await client.post("/api/v1/grocery/clear-checked")
    assert res.json()["deleted_count"] == 0


# ---------------------------------------------------------------------------
# 8. Cross-user isolation
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_cross_user_isolation(db_session: AsyncSession) -> None:
    async for client_a in _make_client(db_session, _USER_A):
        await client_a.post("/api/v1/grocery/", json=_VALID_ITEM)

    async for client_b in _make_client(db_session, _USER_B):
        res = await client_b.get("/api/v1/grocery/")
        assert res.json() == []
