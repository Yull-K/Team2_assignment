from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from wapang.app.items.models import Item
from wapang.app.stores.models import Store
from wapang.app.users.models import User


ITEM_BODY = {"item_name": "waffle", "price": 10000, "stock": 10}


@pytest.fixture
def owned_store(db_session: Session, user: User) -> Store:
    store = Store(
        user_id=user.id,
        name="test store",
        address="Seoul",
        email="store@example.com",
        phone_number="010-1234-5678",
        delivery_fee=3000,
    )
    db_session.add(store)
    db_session.flush()
    return store


def add_item(
    db_session: Session,
    store_id: str,
    *,
    name: str = "waffle",
    price: int = 10000,
    stock: int = 10,
) -> Item:
    item = Item(store_id=store_id, name=name, price=price, stock=stock)
    db_session.add(item)
    db_session.flush()
    return item


def make_foreign_store(db_session: Session) -> Store:
    owner = User(
        email=f"other-{uuid4()}@example.com",
        hashed_password="not-used",
    )
    db_session.add(owner)
    db_session.flush()

    store = Store(
        user_id=owner.id,
        name=f"other-{uuid4()}",
        address="Busan",
        email=f"other-store-{uuid4()}@example.com",
        phone_number=f"010-{uuid4().int % 10000:04d}-{uuid4().int % 10000:04d}",
        delivery_fee=2500,
    )
    db_session.add(store)
    db_session.flush()
    return store


def auth_headers(access_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {access_token}"}


def assert_error(response, status_code: int, code: str, message: str) -> None:
    assert response.status_code == status_code
    assert response.json() == {"error_code": code, "error_msg": message}


def test_add_item(client: TestClient, access_token: str, owned_store: Store):
    response = client.post(
        "/api/items",
        json=ITEM_BODY,
        headers=auth_headers(access_token),
    )

    assert response.status_code == 201
    body = response.json()
    assert body["id"]
    assert body["item_name"] == "waffle"
    assert body["price"] == 10000
    assert body["stock"] == 10


@pytest.mark.parametrize(
    "body",
    [
        {"price": 100, "stock": 1},
        {"item_name": "x", "price": 100, "stock": 1},
        {"item_name": "waffle", "price": -1, "stock": 1},
        {"item_name": "waffle", "price": 100, "stock": -1},
        {"item_name": "waffle", "price": True, "stock": 1},
        {"item_name": "w" * 51, "price": 100, "stock": 1},
    ],
)
def test_add_item_invalid_body(
    client: TestClient,
    access_token: str,
    owned_store: Store,
    body: dict,
):
    response = client.post(
        "/api/items",
        json=body,
        headers=auth_headers(access_token),
    )

    assert response.status_code == 400
    assert response.json()["error_code"] in {"ERR_002", "ERR_003"}


def test_add_item_without_store(client: TestClient, access_token: str):
    response = client.post(
        "/api/items",
        json=ITEM_BODY,
        headers=auth_headers(access_token),
    )

    assert_error(response, 403, "ERR_011", "NO STORE OWNED")


@pytest.mark.parametrize(
    ("method", "path", "body"),
    [
        ("post", "/api/items", ITEM_BODY),
        ("patch", "/api/items/some-id", {"price": 12000}),
        ("delete", "/api/items/some-id", None),
    ],
)
def test_item_mutations_require_authentication(
    client: TestClient, method: str, path: str, body: dict | None
):
    request_options = {}
    if body is not None:
        request_options["json"] = body
    response = client.request(method, path, **request_options)

    assert_error(response, 401, "ERR_005", "UNAUTHENTICATED")


@pytest.mark.parametrize(
    ("method", "path", "body"),
    [
        ("post", "/api/items", ITEM_BODY),
        ("patch", "/api/items/some-id", {"price": 12000}),
        ("delete", "/api/items/some-id", None),
    ],
)
def test_item_mutations_reject_bad_authorization_header(
    client: TestClient,
    access_token: str,
    method: str,
    path: str,
    body: dict | None,
):
    request_options = {"headers": {"Authorization": access_token}}
    if body is not None:
        request_options["json"] = body
    response = client.request(method, path, **request_options)

    assert_error(response, 400, "ERR_006", "BAD AUTHORIZATION HEADER")


@pytest.mark.parametrize(
    ("method", "path", "body"),
    [
        ("post", "/api/items", ITEM_BODY),
        ("patch", "/api/items/some-id", {"price": 12000}),
        ("delete", "/api/items/some-id", None),
    ],
)
def test_item_mutations_reject_invalid_token(
    client: TestClient, method: str, path: str, body: dict | None
):
    request_options = {"headers": {"Authorization": "Bearer invalid-token"}}
    if body is not None:
        request_options["json"] = body
    response = client.request(method, path, **request_options)

    assert_error(response, 401, "ERR_007", "INVALID TOKEN")


def test_update_item_partial(
    client: TestClient,
    db_session: Session,
    access_token: str,
    owned_store: Store,
):
    item = add_item(db_session, owned_store.id)

    response = client.patch(
        f"/api/items/{item.id}",
        json={"price": 15000},
        headers=auth_headers(access_token),
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": item.id,
        "item_name": "waffle",
        "price": 15000,
        "stock": 10,
    }


@pytest.mark.parametrize(
    "body",
    [
        {},
        {"item_name": "x"},
        {"price": -1},
        {"stock": -1},
        {"item_name": None},
        {"unknown": "field"},
    ],
)
def test_update_item_invalid_body(
    client: TestClient,
    db_session: Session,
    access_token: str,
    owned_store: Store,
    body: dict,
):
    item = add_item(db_session, owned_store.id)
    response = client.patch(
        f"/api/items/{item.id}",
        json=body,
        headers=auth_headers(access_token),
    )

    assert response.status_code == 400
    assert response.json()["error_code"] in {"ERR_002", "ERR_003"}


def test_update_item_not_found(
    client: TestClient,
    access_token: str,
    owned_store: Store,
):
    response = client.patch(
        "/api/items/missing",
        json={"price": 12000},
        headers=auth_headers(access_token),
    )

    assert_error(response, 404, "ERR_013", "ITEM NOT FOUND")


def test_update_item_not_owned(
    client: TestClient,
    db_session: Session,
    access_token: str,
    owned_store: Store,
):
    other_store = make_foreign_store(db_session)
    item = add_item(db_session, other_store.id)

    response = client.patch(
        f"/api/items/{item.id}",
        json={"price": 12000},
        headers=auth_headers(access_token),
    )

    assert_error(response, 403, "ERR_014", "NOT YOUR ITEM")


def test_update_item_without_store(
    client: TestClient,
    access_token: str,
):
    response = client.patch(
        "/api/items/some-id",
        json={"price": 12000},
        headers=auth_headers(access_token),
    )

    assert_error(response, 403, "ERR_011", "NO STORE OWNED")


def test_list_items_and_filters(
    client: TestClient,
    db_session: Session,
    owned_store: Store,
):
    add_item(db_session, owned_store.id, name="waffle", price=100, stock=3)
    add_item(db_session, owned_store.id, name="syrup", price=300, stock=0)
    expected = add_item(
        db_session, owned_store.id, name="waffle cake", price=500, stock=2
    )
    other_store = make_foreign_store(db_session)
    add_item(db_session, other_store.id, name="other item", price=500, stock=2)

    response = client.get(
        "/api/items",
        params={
            "store_id": owned_store.id,
            "min_price": 200,
            "max_price": 500,
            "in_stock": "true",
        },
    )

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": expected.id,
            "item_name": "waffle cake",
            "price": 500,
            "stock": 2,
            "store_id": owned_store.id,
            "store_name": "test store",
        }
    ]


def test_list_items_store_not_found(client: TestClient):
    response = client.get("/api/items", params={"store_id": "missing"})

    assert_error(response, 404, "ERR_010", "STORE NOT FOUND")


def test_delete_item(
    client: TestClient,
    db_session: Session,
    access_token: str,
    owned_store: Store,
):
    item = add_item(db_session, owned_store.id)

    response = client.delete(
        f"/api/items/{item.id}",
        headers=auth_headers(access_token),
    )

    assert response.status_code == 204
    assert response.content == b""
    assert db_session.get(Item, item.id) is None


def test_delete_item_not_found(
    client: TestClient,
    access_token: str,
    owned_store: Store,
):
    response = client.delete(
        "/api/items/missing",
        headers=auth_headers(access_token),
    )

    assert_error(response, 404, "ERR_013", "ITEM NOT FOUND")


def test_delete_item_not_owned(
    client: TestClient,
    db_session: Session,
    access_token: str,
    owned_store: Store,
):
    other_store = make_foreign_store(db_session)
    item = add_item(db_session, other_store.id)

    response = client.delete(
        f"/api/items/{item.id}",
        headers=auth_headers(access_token),
    )

    assert_error(response, 403, "ERR_014", "NOT YOUR ITEM")
