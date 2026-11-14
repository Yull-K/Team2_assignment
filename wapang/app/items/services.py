from typing import Annotated

from fastapi import Depends

from wapang.app.items.exceptions import (
    ItemNotFoundException,
    NoStoreOwnedException,
    NotYourItemException,
    StoreNotFoundException,
)
from wapang.app.items.models import Item
from wapang.app.items.repositories import ItemRepository


class ItemService:
    def __init__(
        self, item_repository: Annotated[ItemRepository, Depends()]
    ) -> None:
        self.item_repository = item_repository

    def create_item(
        self, user_id: str, name: str, price: int, stock: int
    ) -> Item:
        store = self.item_repository.get_store_owned_by(user_id)
        if store is None:
            raise NoStoreOwnedException()

        return self.item_repository.create_item(
            store_id=store.id,
            name=name,
            price=price,
            stock=stock,
        )

    def update_item(
        self,
        user_id: str,
        item_id: str,
        name: str | None,
        price: int | None,
        stock: int | None,
    ) -> Item:
        store = self.item_repository.get_store_owned_by(user_id)
        if store is None:
            raise NoStoreOwnedException()

        item = self.item_repository.get_item_by_id(item_id)
        if item is None:
            raise ItemNotFoundException()
        if item.store_id != store.id:
            raise NotYourItemException()

        return self.item_repository.update_item(item, name, price, stock)

    def list_items(
        self,
        store_id: str | None,
        min_price: int | None,
        max_price: int | None,
        in_stock: bool,
    ) -> list[Item]:
        if (
            store_id is not None
            and self.item_repository.get_store_by_id(store_id) is None
        ):
            raise StoreNotFoundException()

        return self.item_repository.list_items(
            store_id=store_id,
            min_price=min_price,
            max_price=max_price,
            in_stock=in_stock,
        )

    def delete_item(self, user_id: str, item_id: str) -> None:
        item = self.item_repository.get_item_by_id(item_id)
        if item is None:
            raise ItemNotFoundException()

        store = self.item_repository.get_store_owned_by(user_id)
        if store is None or item.store_id != store.id:
            raise NotYourItemException()

        self.item_repository.delete_item(item)
