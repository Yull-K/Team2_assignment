from typing import Annotated

from fastapi import Depends

from wapang.app.orders.exceptions import ItemNotFoundException, NotEnoughStockException
from wapang.app.orders.models import Order
from wapang.app.orders.repositories import OrderRepository
from wapang.app.orders.schemas import (
    OrderItemDetail,
    OrderItemRequest,
    OrderResponse,
    StoreOrderDetail,
)


class OrderService:
    def __init__(self, order_repository: Annotated[OrderRepository, Depends()]) -> None:
        self.order_repository = order_repository

    def create_order(self, user_id: str, items: list[OrderItemRequest]) -> Order:
        item_ids = [request.item_id for request in items]
        found_items = {
            item.id: item for item in self.order_repository.get_items_by_ids(item_ids)
        }

        # 1) 상품이 전부 있는지 먼저 확인
        for request in items:
            if request.item_id not in found_items:
                raise ItemNotFoundException()

        # 2) 재고 확인
        items_with_quantity = []
        for request in items:
            item = found_items[request.item_id]
            if item.stock < request.quantity:
                raise NotEnoughStockException()
            items_with_quantity.append((item, request.quantity))

        # 3) 상점별 금액 = 배달비 + 상품 합계
        store_totals: dict[str, int] = {}
        for item, quantity in items_with_quantity:
            if item.store_id not in store_totals:
                store_totals[item.store_id] = item.store.delivery_fee
            store_totals[item.store_id] += item.price * quantity
        total_price = sum(store_totals.values())

        return self.order_repository.create_order(user_id, total_price, items_with_quantity)

    def build_order_response(self, order: Order) -> OrderResponse:
        groups: dict[str, StoreOrderDetail] = {}

        for order_item in order.order_items:
            subtotal = order_item.price * order_item.quantity

            if order_item.store_id not in groups:
                groups[order_item.store_id] = StoreOrderDetail(
                    store_id=order_item.store_id,
                    store_name=order_item.store.name,
                    delivery_fee=order_item.store.delivery_fee,
                    store_total_price=order_item.store.delivery_fee,
                    items=[],
                )

            group = groups[order_item.store_id]
            group.items.append(
                OrderItemDetail(
                    item_id=order_item.item_id,
                    item_name=order_item.item_name,
                    price=order_item.price,
                    quantity=order_item.quantity,
                    subtotal=subtotal,
                )
            )
            group.store_total_price += subtotal

        return OrderResponse(
            order_id=order.id,
            details=list(groups.values()),
            total_price=order.total_price,
            status=order.status,
        )