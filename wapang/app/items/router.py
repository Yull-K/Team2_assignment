from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from wapang.app.auth.utils import login_with_header
from wapang.app.items.schemas import (
    AddItemRequest,
    ItemListResponse,
    ItemResponse,
    UpdateItemRequest,
)
from wapang.app.items.services import ItemService
from wapang.app.users.models import User


item_router = APIRouter()


@item_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=ItemResponse,
)
def add_item(
    request: AddItemRequest,
    user: Annotated[User, Depends(login_with_header)],
    item_service: Annotated[ItemService, Depends()],
) -> ItemResponse:
    item = item_service.create_item(
        user_id=user.id,
        name=request.item_name,
        price=request.price,
        stock=request.stock,
    )
    return ItemResponse.model_validate(item)


@item_router.patch("/{item_id}", response_model=ItemResponse)
def update_item(
    item_id: str,
    request: UpdateItemRequest,
    user: Annotated[User, Depends(login_with_header)],
    item_service: Annotated[ItemService, Depends()],
) -> ItemResponse:
    item = item_service.update_item(
        user_id=user.id,
        item_id=item_id,
        name=request.item_name,
        price=request.price,
        stock=request.stock,
    )
    return ItemResponse.model_validate(item)


@item_router.get("/", response_model=list[ItemListResponse])
def list_items(
    item_service: Annotated[ItemService, Depends()],
    store_id: str | None = None,
    min_price: int | None = Query(default=None, ge=0),
    max_price: int | None = Query(default=None, ge=0),
    in_stock: bool = False,
) -> list[ItemListResponse]:
    items = item_service.list_items(
        store_id=store_id,
        min_price=min_price,
        max_price=max_price,
        in_stock=in_stock,
    )
    return [ItemListResponse.model_validate(item) for item in items]


@item_router.delete(
    "/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_item(
    item_id: str,
    user: Annotated[User, Depends(login_with_header)],
    item_service: Annotated[ItemService, Depends()],
) -> None:
    item_service.delete_item(user_id=user.id, item_id=item_id)
