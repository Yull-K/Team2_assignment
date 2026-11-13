from typing import Annotated
import uuid

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from wapang.app.users.models import User
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