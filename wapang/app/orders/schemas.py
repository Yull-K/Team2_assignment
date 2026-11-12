from pydantic import BaseModel, Field, field_validator

from wapang.app.orders.exceptions import EmptyItemListException
from wapang.app.orders.models import OrderStatus
from wapang.common.exceptions import InvalidFormatException


# ---------- 요청 ----------
class OrderItemRequest(BaseModel):
    item_id: str
    quantity: int = Field(strict=True)

    @field_validator("quantity", mode="after")
    def validate_quantity(cls, v):
        if v < 1:
            raise InvalidFormatException()
        return v


class OrderCreateRequest(BaseModel):
    items: list[OrderItemRequest]

    @field_validator("items", mode="after")
    def validate_items(cls, v):
        if len(v) == 0:
            raise EmptyItemListException()
        item_ids = [item.item_id for item in v]
        if len(item_ids) != len(set(item_ids)):
            raise InvalidFormatException()
        return v


# ---------- 응답 ----------
class OrderItemDetail(BaseModel):
    item_id: str | None
    item_name: str
    price: int
    quantity: int
    subtotal: int


class StoreOrderDetail(BaseModel):
    store_id: str
    store_name: str
    delivery_fee: int
    store_total_price: int
    items: list[OrderItemDetail]


class OrderResponse(BaseModel):
    order_id: str
    details: list[StoreOrderDetail]
    total_price: int
    status: OrderStatus