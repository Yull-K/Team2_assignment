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

class OrderStatus(str, enum.Enum):
    CANCELED = "CANCELED"
    ORDERED = "ORDERED"
    COMPLETE = "COMPLETE"


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid7())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id"), index=True, nullable=False
    )
    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus, name="order_status"),
        nullable=False,
        default=OrderStatus.ORDERED,
    )
    total_price: Mapped[int] = mapped_column(BigInteger, nullable=False)

    user: Mapped["User"] = relationship(back_populates="orders")
    order_items: Mapped[list["OrderItem"]] = relationship(
        back_populates="order"
    )


class OrderItem(Base):
    __tablename__ = "order_items"
    __table_args__ = (
        UniqueConstraint("order_id", "item_id", name="uq_order_item"),
        CheckConstraint("quantity >= 1", name="check_order_item_quantity_min"),
        CheckConstraint("price >= 0", name="check_order_item_price_min"),
    )

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid7())
    )
    order_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("orders.id"), index=True, nullable=False
    )
    # 상품이 삭제되면 NULL로 바뀜 (주문 기록은 유지)
    item_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("items.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    # 주문 당시 정보 복사본 (상품이 삭제돼도 주문 조회 가능)
    item_name: Mapped[str] = mapped_column(String(50), nullable=False)
    price: Mapped[int] = mapped_column(BigInteger, nullable=False)
    store_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("stores.id"), index=True, nullable=False
    )
    quantity: Mapped[int] = mapped_column(BigInteger, nullable=False)

    order: Mapped["Order"] = relationship(back_populates="order_items")
    item: Mapped["Item | None"] = relationship(back_populates="order_items")
    store: Mapped["Store"] = relationship()
