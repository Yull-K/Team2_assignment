from typing import Annotated

from fastapi import APIRouter, Depends, Response, status

from wapang.app.auth.utils import login_with_header
from wapang.app.orders.schemas import (
    OrderCreateRequest,
    OrderResponse,
    OrderStatusUpdateRequest,
)
from wapang.app.orders.services import OrderService
from wapang.app.users.models import User

order_router = APIRouter()


@order_router.post("", status_code=status.HTTP_201_CREATED)
def create_order(
    create_request: OrderCreateRequest,
    user: Annotated[User, Depends(login_with_header)],
    order_service: Annotated[OrderService, Depends()],
) -> OrderResponse:
    order = order_service.create_order(user.id, create_request.items)
    return order_service.build_order_response(order)


@order_router.get("/{order_id}")
def get_order(
    order_id: str,
    user: Annotated[User, Depends(login_with_header)],
    order_service: Annotated[OrderService, Depends()],
) -> OrderResponse:
    order = order_service.get_my_order(user.id, order_id)
    return order_service.build_order_response(order)


@order_router.patch("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def update_order_status(
    order_id: str,
    update_request: OrderStatusUpdateRequest,
    user: Annotated[User, Depends(login_with_header)],
    order_service: Annotated[OrderService, Depends()],
) -> Response:
    order_service.update_order_status(user.id, order_id, update_request.status)
    return Response(status_code=status.HTTP_204_NO_CONTENT)