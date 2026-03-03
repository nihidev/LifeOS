from uuid import UUID

from fastapi import APIRouter, status

from app.core.deps import CurrentUser, DB
from app.schemas.grocery import (
    ClearCheckedResponse,
    GroceryItemCreate,
    GroceryItemResponse,
    GroceryItemUpdate,
)
from app.services import grocery_service as service

router = APIRouter()


@router.post("/", response_model=GroceryItemResponse, status_code=status.HTTP_201_CREATED)
async def add_item(
    body: GroceryItemCreate,
    db: DB,
    user_id: CurrentUser,
) -> GroceryItemResponse:
    return await service.add_item(db, user_id, body)


@router.get("/", response_model=list[GroceryItemResponse])
async def list_items(
    db: DB,
    user_id: CurrentUser,
) -> list[GroceryItemResponse]:
    return await service.list_items(db, user_id)


# NOTE: must be registered before /{id} to avoid FastAPI matching "clear-checked" as a UUID
@router.post("/clear-checked", response_model=ClearCheckedResponse)
async def clear_checked(
    db: DB,
    user_id: CurrentUser,
) -> ClearCheckedResponse:
    return await service.clear_checked(db, user_id)


@router.patch("/{id}", response_model=GroceryItemResponse)
async def update_item(
    id: UUID,
    body: GroceryItemUpdate,
    db: DB,
    user_id: CurrentUser,
) -> GroceryItemResponse:
    return await service.update_item(db, user_id, id, body)


@router.delete("/{id}", status_code=status.HTTP_200_OK)
async def delete_item(
    id: UUID,
    db: DB,
    user_id: CurrentUser,
) -> dict[str, str]:
    return await service.delete_item(db, user_id, id)
