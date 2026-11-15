from typing import Annotated
from fastapi import APIRouter, Depends, status

from wapang.app.auth.utils import login_with_header

from wapang.app.users.models import User

from wapang.app.users.schemas import UserSignupRequest, UserUpdateRequest, UserResponse
from wapang.app.orders.schemas import OrderSummaryResponse

from wapang.app.users.services import UserService
from wapang.app.orders.services import OrderService

user_router = APIRouter()

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

