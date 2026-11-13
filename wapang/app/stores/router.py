from typing import Annotated
from fastapi import APIRouter, Depends, status

from wapang.app.auth.utils import login_with_header

from wapang.app.users.models import User

from wapang.app.stores.schemas import StoreAddRequest, StoreResponse, StoreUpdateRequest, ItemResponse

from wapang.app.stores.services import StoreService

store_router = APIRouter()

@store_router.post("/", status_code=status.HTTP_201_CREATED)
def add_store(
    add_request: StoreAddRequest, 
    # 유저 토큰 확인
    user: Annotated[User, Depends(login_with_header)],
    store_service: Annotated[StoreService, Depends()]
) -> StoreResponse:
    store = store_service.create_store(
        user.id,
        add_request.store_name, 
        add_request.address, 
        add_request.email, 
        add_request.phone_number, 
        add_request.delivery_fee
    )
    return StoreResponse(
        id=store.id,
        store_name = store.store_name,
        address = store.address,
        email=store.email,
        phone_number=store.phone_number,
        delivery_fee=store.delivery_fee
    )

@store_router.patch("/{store_id}")
def update_store(
    store_id: str,
    update_request: StoreUpdateRequest,
    user: Annotated[User, Depends(login_with_header)],
    store_service: Annotated[StoreService, Depends()]
) -> StoreResponse:
    updated_store = store_service.update_store(
        store_id,
        user.id,
        update_request.store_name,
        update_request.address,
        update_request.email,
        update_request.phone_number,
        update_request.delivery_fee
    )
    return StoreResponse.model_validate(updated_store)

    
@store_router.get("/{store_id}")
def get_store(
    store_id: str,
    store_service: Annotated[StoreService, Depends()]
) -> StoreResponse:
    store = store_service.get_store_by_id(store_id)
    return StoreResponse.model_validate(store)

@store_router.get("/{store_id}/items")
def get_items(
    store_id: str,
    store_service: Annotated[StoreService, Depends()]
) -> list[ItemResponse]:
    items = store_service.get_store_items(store_id)
    return [ItemResponse.model_validate(item) for item in items]
