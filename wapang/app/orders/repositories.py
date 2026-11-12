from typing import Annotated

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from wapang.app.items.models import Item
from wapang.app.orders.models import Order, OrderItem
from wapang.database.connection import get_db_session


class OrderRepository:
    def __init__(self, session: Annotated[Session, Depends(get_db_session)]) -> None:
        self.session = session

    def get_items_by_ids(self, item_ids: list[str]) -> list[Item]:
        return list(
            self.session.scalars(
                select(Item).where(Item.id.in_(item_ids)).with_for_update()
            )
        )

    def create_order(
        self,
        user_id: str,
        total_price: int,
        items_with_quantity: list[tuple[Item, int]],
    ) -> Order:
        order = Order(user_id=user_id, total_price=total_price)

        for item, quantity in items_with_quantity:
            order.order_items.append(
                OrderItem(
                    item=item,
                    item_name=item.name,
                    price=item.price,
                    store_id=item.store_id,
                    quantity=quantity,
                )
            )
            item.stock -= quantity

        self.session.add(order)
        self.session.flush()

        return order