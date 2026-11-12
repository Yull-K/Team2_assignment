import enum
from uuid6 import uuid7

from sqlalchemy import (
    BigInteger,
    Enum,
    ForeignKey,
    String,
    UniqueConstraint,
    CheckConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship, synonym

from wapang.database.common import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid7())
    )
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(100))
    nickname: Mapped[str | None] = mapped_column(String(20))
    address: Mapped[str | None] = mapped_column(String(100))
    phone_number: Mapped[str | None] = mapped_column(String(20))

    # 유저는 상점을 최대 하나 소유할 수 있음
    store: Mapped["Store | None"] = relationship(back_populates="user")

    # 유저는 여러 주문을 할 수 있음
    orders: Mapped[list["Order"]] = relationship(back_populates="user")
