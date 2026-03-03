from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import grocery_repository as repo
from app.schemas.grocery import (
    ClearCheckedResponse,
    GroceryItemCreate,
    GroceryItemResponse,
    GroceryItemUpdate,
)


async def add_item(
    db: AsyncSession, user_id: UUID, data: GroceryItemCreate
) -> GroceryItemResponse:
    item = await repo.create(db, user_id, data)
    return GroceryItemResponse.model_validate(item)


async def list_items(
    db: AsyncSession, user_id: UUID
) -> list[GroceryItemResponse]:
    items = await repo.get_all(db, user_id)
    return [GroceryItemResponse.model_validate(i) for i in items]


async def update_item(
    db: AsyncSession, user_id: UUID, id: UUID, data: GroceryItemUpdate
) -> GroceryItemResponse:
    item = await repo.update(db, user_id, id, data)
    if item is None:
        raise HTTPException(status_code=404, detail="Grocery item not found")
    return GroceryItemResponse.model_validate(item)


async def delete_item(
    db: AsyncSession, user_id: UUID, id: UUID
) -> dict[str, str]:
    deleted = await repo.delete_item(db, user_id, id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Grocery item not found")
    return {"message": "deleted"}


async def clear_checked(
    db: AsyncSession, user_id: UUID
) -> ClearCheckedResponse:
    count = await repo.clear_checked(db, user_id)
    return ClearCheckedResponse(deleted_count=count)
