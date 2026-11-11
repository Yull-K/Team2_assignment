import enum

from uuid6 import uuid7
from sqlalchemy import Enum, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from wapang.database.common import Base


class OrderStatus(str, enum.Enum):
    CANCELED = "CANCELED"
    ORDERED = "ORDERED"
    COMPLETE = "COMPLETE"


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid7()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), index=True)
    status: Mapped[OrderStatus] = mapped_column(Enum(OrderStatus), default=OrderStatus.ORDERED)
    total_price: Mapped[int] = mapped_column(Integer)

    user: Mapped["User"] = relationship(back_populates="orders")
    order_items: Mapped[list["OrderItem"]] = relationship(back_populates="order")


class OrderItem(Base):
    __tablename__ = "order_items"
    __table_args__ = (UniqueConstraint("order_id", "item_id"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid7()))
    order_id: Mapped[str] = mapped_column(String(36), ForeignKey("orders.id"), index=True)
    item_id: Mapped[str] = mapped_column(String(36), ForeignKey("items.id"), index=True)
    quantity: Mapped[int] = mapped_column(Integer)
    price: Mapped[int] = mapped_column(Integer)

    order: Mapped["Order"] = relationship(back_populates="order_items")
    item: Mapped["Item"] = relationship()