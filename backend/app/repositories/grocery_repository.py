from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.grocery_item import GroceryItem
from app.schemas.grocery import GroceryItemCreate, GroceryItemUpdate


async def create(
    db: AsyncSession, user_id: UUID, data: GroceryItemCreate
) -> GroceryItem:
    item = GroceryItem(
        user_id=user_id,
        item=data.item,
        quantity=data.quantity,
    )
    db.add(item)
    await db.flush()
    await db.refresh(item)
    return item


async def get_all(db: AsyncSession, user_id: UUID) -> list[GroceryItem]:
    result = await db.execute(
        select(GroceryItem)
        .where(GroceryItem.user_id == user_id)
        .order_by(GroceryItem.checked.asc(), GroceryItem.created_at.asc())
    )
    return list(result.scalars().all())


async def get_by_id(
    db: AsyncSession, user_id: UUID, id: UUID
) -> GroceryItem | None:
    result = await db.execute(
        select(GroceryItem).where(
            GroceryItem.id == id, GroceryItem.user_id == user_id
        )
    )
    return result.scalar_one_or_none()


async def update(
    db: AsyncSession, user_id: UUID, id: UUID, data: GroceryItemUpdate
) -> GroceryItem | None:
    item = await get_by_id(db, user_id, id)
    if item is None:
        return None
    if data.item is not None:
        item.item = data.item
    if data.quantity is not None:
        item.quantity = data.quantity
    if data.checked is not None:
        item.checked = data.checked
    await db.flush()
    await db.refresh(item)
    return item


async def delete_item(db: AsyncSession, user_id: UUID, id: UUID) -> bool:
    item = await get_by_id(db, user_id, id)
    if item is None:
        return False
    await db.delete(item)
    await db.flush()
    return True


async def clear_checked(db: AsyncSession, user_id: UUID) -> int:
    result = await db.execute(
        select(GroceryItem).where(
            GroceryItem.user_id == user_id, GroceryItem.checked.is_(True)
        )
    )
    items = list(result.scalars().all())
    for item in items:
        await db.delete(item)
    await db.flush()
    return len(items)
