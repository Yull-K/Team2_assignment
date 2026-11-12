from typing import Annotated

from fastapi import APIRouter, Depends, status

from wapang.app.auth.utils import login_with_header
from wapang.app.orders.schemas import OrderCreateRequest, OrderResponse
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