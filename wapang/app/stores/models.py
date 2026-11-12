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

class Store(Base):
    __tablename__ = "stores"
    __table_args__ = (
        # 3글자 이상 제약조건 (ERD / README 요구사항: 3글자 이상 20글자 이하)
        # ---------------------------------------------
        CheckConstraint(
            "CHAR_LENGTH(name) >= 3",
            name="check_store_name_min_length_mysql",
        ).ddl_if(dialect="mysql"),
        CheckConstraint(
            "length(name) >= 3",
            name="check_store_name_min_length_sqlite",
        ).ddl_if(dialect="sqlite"),
        # ---------------------------------------------
        CheckConstraint("delivery_fee >= 0", name="check_devliery_fee"),
    )

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid7())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), unique=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    address: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    phone_number: Mapped[str] = mapped_column(
        String(20), unique=True, nullable=False
    )
    delivery_fee: Mapped[int] = mapped_column(
        BigInteger, nullable=False, default=0
    )

    # API에서 store_name을 사용할 때 name과 연결
    store_name = synonym("name")

    user: Mapped["User"] = relationship(back_populates="store")
    items: Mapped[list["Item"]] = relationship(back_populates="store")
