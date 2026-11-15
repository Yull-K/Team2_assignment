from typing import Annotated

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from wapang.app.items.models import Item
from wapang.app.stores.models import Store
from wapang.database.connection import get_db_session


class ItemRepository:
    def __init__(
        self, session: Annotated[Session, Depends(get_db_session)]
    ) -> None:
        self.session = session

    def get_store_by_id(self, store_id: str) -> Store | None:
        return self.session.get(Store, store_id)

    def get_store_owned_by(self, user_id: str) -> Store | None:
        return self.session.scalar(select(Store).where(Store.user_id == user_id))

    def get_item_by_id(self, item_id: str) -> Item | None:
        statement = (
            select(Item)
            .options(joinedload(Item.store))
            .where(Item.id == item_id)
        )
        return self.session.scalar(statement)

    def create_item(
        self, store_id: str, name: str, price: int, stock: int
    ) -> Item:
        item = Item(
            store_id=store_id,
            name=name,
            price=price,
            stock=stock,
        )
        self.session.add(item)
        self.session.flush()
        return item

    def list_items(
        self,
        store_id: str | None,
        min_price: int | None,
        max_price: int | None,
        in_stock: bool,
    ) -> list[Item]:
        statement = select(Item).options(joinedload(Item.store))

        if store_id is not None:
            statement = statement.where(Item.store_id == store_id)
        if min_price is not None:
            statement = statement.where(Item.price >= min_price)
        if max_price is not None:
            statement = statement.where(Item.price <= max_price)
        if in_stock:
            statement = statement.where(Item.stock > 0)

        statement = statement.order_by(Item.id)
        return list(self.session.scalars(statement).all())

    def update_item(
        self,
        item: Item,
        name: str | None,
        price: int | None,
        stock: int | None,
    ) -> Item:
        if name is not None:
            item.name = name
        if price is not None:
            item.price = price
        if stock is not None:
            item.stock = stock

        self.session.flush()
        return item

    def delete_item(self, item: Item) -> None:
        self.session.delete(item)
        self.session.flush()
