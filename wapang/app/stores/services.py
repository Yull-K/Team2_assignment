from typing import Annotated

from fastapi import Depends
from wapang.app.stores.models import Store
from wapang.app.items.models import Item
from wapang.app.stores.repositories import StoreRepository
from wapang.app.stores.exceptions import StoreAlreadyExistsException, StoreInfoConflictException, StoreNotFoundException, NoStoreOwnedException, NotYourStoreException
    
class StoreService:
    def __init__(self, store_repository: Annotated[StoreRepository, Depends()]) -> None:
        self.store_repository = store_repository
    
    def create_store(
            self, 
            user_id: str,
            store_name: str,
            address: str,
            email: str,
            phone_number: str,
            delivery_fee: int
        ) -> Store:

        # 이미 상점을 소유하고 있는 경우
        if self.store_repository.get_store_by_user_id(user_id):
            raise StoreAlreadyExistsException()
        
        # 상점명/이메일/전화번호가 중복되는 경우
        if self.store_repository.get_store_by_name(store_name):
            raise StoreInfoConflictException()
        if self.store_repository.get_store_by_email(email):
            raise StoreInfoConflictException()
        if self.store_repository.get_store_by_phone_number(phone_number):
            raise StoreInfoConflictException()
        
        return self.store_repository.create_store(user_id, store_name,address, email, phone_number, delivery_fee)
    
    def get_store_by_id(self, store_id: str) -> Store:
        store = self.store_repository.get_store_by_id(store_id)
        if store is None:
            raise StoreNotFoundException()
        return store
    
    def update_store(
        self, 
        store_id: str,
        user_id: str,
        store_name: str | None,
        address: str | None,
        email: str | None,
        phone_number: str | None,
        delivery_fee: int | None
    ) -> Store:
        
        # 상점을 소유하지 않은 경우
        if self.store_repository.get_store_by_user_id(user_id) is None:
            raise NoStoreOwnedException()

        # 상점이 존재하지 않는 경우
        store = self.get_store_by_id(store_id)
        
        # 다른 상점을 수정하려는 경우
        if store.user_id != user_id:
            raise NotYourStoreException()

        # 상점명/이메일/전화번호가 중복되는 경우
        if store_name is not None:
            existing = self.store_repository.get_store_by_name(store_name)
            if existing and existing.id != store.id:
                raise StoreInfoConflictException()
        if email is not None:
            existing = self.store_repository.get_store_by_email(email)
            if existing and existing.id != store.id:
                raise StoreInfoConflictException()
        if phone_number is not None:
            existing = self.store_repository.get_store_by_phone_number(phone_number)
            if existing and existing.id != store.id:
                raise StoreInfoConflictException()

        return self.store_repository.update_store(store, store_name, address, email, phone_number, delivery_fee)
    
    def get_store_items(self, store_id: str) -> list[Item]:
        store = self.get_store_by_id(store_id)
        return store.items