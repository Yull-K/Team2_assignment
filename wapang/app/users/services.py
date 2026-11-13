from typing import Annotated
from argon2 import PasswordHasher

from fastapi import Depends
from wapang.app.users.models import User, Store, Item
from wapang.app.users.repositories import UserRepository, StoreRepository
from wapang.app.users.exceptions import EmailAlreadyExistsException
from wapang.app.users.exceptions import StoreAlreadyExistsException, StoreInfoConflictException, StoreNotFoundException, NoStoreOwnedException, NotYourStoreException

class UserService:
    def __init__(self, user_repository: Annotated[UserRepository, Depends()]) -> None:
        self.user_repository = user_repository

    def create_user(self, email: str, password: str) -> User:        
        if self.user_repository.get_user_by_email(email):
            raise EmailAlreadyExistsException()

        hashed_password = PasswordHasher().hash(password)

        return self.user_repository.create_user(email, hashed_password)

    def get_user_by_id(self, user_id: str) -> User | None:
        return self.user_repository.get_user_by_id(user_id)

    def update_user(
        self,
        user_id: str,
        nickname: str | None,
        address: str | None,
        phone_number: str | None,
    ) -> User:
        user = self.user_repository.get_user_by_id(user_id)
        return self.user_repository.update_user(user, nickname, address, phone_number)
    
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