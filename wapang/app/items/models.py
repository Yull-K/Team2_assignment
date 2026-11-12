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

class Item(Base):
    __tablename__ = "items"
    __table_args__ = (
        # ---------------------------------------------
        CheckConstraint(
            "CHAR_LENGTH(name) >= 2",
            name="check_item_name_min_length_mysql",
        ).ddl_if(dialect="mysql"),
        CheckConstraint(
            "length(name) >= 2",
            name="check_item_name_min_length_sqlite",
        ).ddl_if(dialect="sqlite"),
        # ---------------------------------------------
        CheckConstraint("price >= 0", name="check_price_min"),
        CheckConstraint("stock >= 0", name="check_stock_min"),
    )

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid7())
    )
    store_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("stores.id"), index=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    price: Mapped[int] = mapped_column(BigInteger, nullable=False)
    stock: Mapped[int] = mapped_column(BigInteger, nullable=False)

    # API에서 item_name을 사용할 때 name과 연결
    item_name = synonym("name")

    store: Mapped["Store"] = relationship(back_populates="items")
    order_items: Mapped[list["OrderItem"]] = relationship(
        back_populates="item"
    )