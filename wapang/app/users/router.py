from typing import Annotated
from fastapi import APIRouter, Depends, status

from wapang.app.auth.utils import login_with_header

from wapang.app.users.models import User

from wapang.app.users.schemas import UserSignupRequest, UserUpdateRequest, UserResponse
from wapang.app.users.schemas import StoreAddRequest, StoreResponse, StoreUpdateRequest, ItemResponse
from wapang.app.orders.schemas import OrderSummaryResponse

from wapang.app.users.services import UserService, StoreService
from wapang.app.orders.services import OrderService

user_router = APIRouter()
store_router = APIRouter()

@user_router.post("/", status_code=status.HTTP_201_CREATED)
def signup(
    signup_request: UserSignupRequest, user_service: Annotated[UserService, Depends()]
) -> UserResponse:
    user = user_service.create_user(
        signup_request.email, signup_request.password,
    )
    return UserResponse(
        id=user.id,
        email=user.email,
        nickname=user.nickname,
        address=user.address,
        phone_number=user.phone_number,
    )

@user_router.get("/me")
def get_me(
    user: Annotated[User, Depends(login_with_header)],
    ) -> UserResponse:
    return UserResponse.model_validate(user)

@user_router.patch("/me")
def update_me(
    update_request: UserUpdateRequest,
    user: Annotated[User, Depends(login_with_header)],
    user_service: Annotated[UserService, Depends()],
) -> UserResponse:
    updated_user = user_service.update_user(
        user.id,
        update_request.nickname,
        update_request.address,
        update_request.phone_number,
    )
    return UserResponse.model_validate(updated_user)

@user_router.get("/me/orders")
def get_my_orders(
    user: Annotated[User, Depends(login_with_header)],
    order_service: Annotated[OrderService, Depends()],
) -> list[OrderSummaryResponse]:
    return order_service.get_my_orders(user.id)

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
