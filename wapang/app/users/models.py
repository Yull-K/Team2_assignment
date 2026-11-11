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