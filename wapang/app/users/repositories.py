from typing import Annotated
import uuid

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from wapang.app.users.models import User, Store
from wapang.database.connection import get_db_session

class UserRepository:
    def __init__(self, session: Annotated[Session, Depends(get_db_session)]) -> None:
        self.session = session

    def create_user(self, email: str, hashed_password: str) -> User:
        user = User(email=email, hashed_password=hashed_password)
        self.session.add(user)

        self.session.flush()
        
        return user

    def get_user_by_id(self, user_id: str) -> User | None:
        return self.session.scalar(select(User).where(User.id == user_id))
    
    def get_user_by_email(self, email: str) -> User | None:
        return self.session.scalar(select(User).where(User.email == email))

    def update_user(
        self,
        user: User,
        nickname: str | None,
        address: str | None,
        phone_number: str | None,
    ) -> User:
        if nickname is not None:
            user.nickname = nickname
        if address is not None:
            user.address = address
        if phone_number is not None:
            user.phone_number = phone_number

        self.session.flush()

        return user
    
class StoreRepository:
    def __init__(self, session: Annotated[Session, Depends(get_db_session)]) -> None:
        self.session = session

    def create_store(
            self, 
            user_id: str,
            store_name: str,
            address: str,
            email: str,
            phone_number: str,
            delivery_fee: int
        ) -> Store:
        store = Store(user_id=user_id,store_name = store_name,address=address,email=email,phone_number=phone_number,delivery_fee=delivery_fee)
        self.session.add(store)
        self.session.flush()
        
        return store

    def update_store(
            self, 
            store: Store,
            store_name: str | None,
            address: str | None,
            email: str | None,
            phone_number: str | None,
            delivery_fee: int | None
        ) -> Store:

        if store_name is not None:
            store.store_name = store_name
        if address is not None:
            store.address = address
        if email is not None:
            store.email = email
        if phone_number is not None:
            store.phone_number = phone_number
        if delivery_fee is not None:
            store.delivery_fee = delivery_fee

        self.session.flush()

        return store
    
    # 한 사용자는 최대 하나의 상점만 소유할 수 있습니다.
    def get_store_by_user_id(self, user_id: str) -> Store | None:
        return self.session.scalar(select(Store).where(Store.user_id == user_id))

    # store_name: 기존에 존재하는 상점과 중복되지 않는지 확인해야 합니다.
    def get_store_by_name(self, store_name: str) -> Store | None:
        return self.session.scalar(select(Store).where(Store.store_name == store_name))

    # email: 기존에 존재하는 상점과 중복되지 않는지 확인해야 합니다.
    def get_store_by_email(self, email: str) -> Store | None:
        return self.session.scalar(select(Store).where(Store.email == email))

    # phone_number: 기존에 존재하는 상점과 중복되지 않는지 확인해야 합니다.
    def get_store_by_phone_number(self, phone_number: str) -> Store | None:
        return self.session.scalar(select(Store).where(Store.phone_number == phone_number))
    
    # 각 상점에는 고유 식별자로 id(str)가 부여됩니다.
    def get_store_by_id(self, store_id: str) -> Store | None:
        return self.session.scalar(select(Store).where(Store.id == store_id))
