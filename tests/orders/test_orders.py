import pytest
from fastapi.testclient import TestClient
from sqlalchemy import orm

from wapang.app.items.models import Item
from wapang.app.stores.models import Store
from wapang.app.users.models import User


# ---------- 준비: 상점 2개 + 상품 2개를 DB에 직접 넣기 ----------
@pytest.fixture
def items(db_session: orm.Session) -> dict[str, Item]:
    owner1 = User(email="owner1@snu.ac.kr", hashed_password="test-hash")
    owner2 = User(email="owner2@snu.ac.kr", hashed_password="test-hash")

    store1 = Store(
        user=owner1, name="와플 스토어", address="서울시 관악구",
        email="waffle@snu.ac.kr", phone_number="010-1111-1111", delivery_fee=3000,
    )
    store2 = Store(
        user=owner2, name="초콜릿 스토어", address="서울시 강남구",
        email="choco@snu.ac.kr", phone_number="010-2222-2222", delivery_fee=2500,
    )

    waffle = Item(store=store1, name="와플", price=10000, stock=5)
    choco = Item(store=store2, name="초콜릿", price=15000, stock=3)

    db_session.add_all([owner1, owner2, store1, store2, waffle, choco])
    db_session.commit()

    return {"waffle": waffle, "choco": choco}


def auth(access_token: str) -> dict:
    return {"Authorization": f"Bearer {access_token}"}


# ---------- TEST POST /api/orders ----------
def test_create_order(client: TestClient, access_token: str, items, db_session):
    req = {
        "items": [
            {"item_id": items["waffle"].id, "quantity": 2},
            {"item_id": items["choco"].id, "quantity": 1},
        ]
    }

    res = client.post("/api/orders", json=req, headers=auth(access_token))
    res_json = res.json()

    assert res.status_code == 201
    assert res_json["order_id"] is not None
    assert res_json["status"] == "ORDERED"
    assert res_json["total_price"] == 40500  # (20000 + 3000) + (15000 + 2500)

    waffle_store = res_json["details"][0]
    assert waffle_store["store_name"] == "와플 스토어"
    assert waffle_store["store_total_price"] == 23000
    assert waffle_store["items"][0]["subtotal"] == 20000

    # 재고가 줄었는지
    db_session.refresh(items["waffle"])
    db_session.refresh(items["choco"])
    assert items["waffle"].stock == 3
    assert items["choco"].stock == 2


def test_create_order_missing_items(client: TestClient, access_token: str):
    res = client.post("/api/orders", json={}, headers=auth(access_token))

    assert res.status_code == 400
    assert res.json()["error_code"] == "ERR_002"


def test_create_order_empty_items(client: TestClient, access_token: str):
    res = client.post("/api/orders", json={"items": []}, headers=auth(access_token))

    assert res.status_code == 422
    assert res.json()["error_code"] == "ERR_018"


def test_create_order_invalid_quantity(client: TestClient, access_token: str, items):
    req = {"items": [{"item_id": items["waffle"].id, "quantity": 0}]}

    res = client.post("/api/orders", json=req, headers=auth(access_token))

    assert res.status_code == 400
    assert res.json()["error_code"] == "ERR_003"


def test_create_order_duplicate_item(client: TestClient, access_token: str, items):
    req = {
        "items": [
            {"item_id": items["waffle"].id, "quantity": 1},
            {"item_id": items["waffle"].id, "quantity": 1},
        ]
    }

    res = client.post("/api/orders", json=req, headers=auth(access_token))

    assert res.status_code == 400
    assert res.json()["error_code"] == "ERR_003"


def test_create_order_item_not_found(client: TestClient, access_token: str, items):
    req = {"items": [{"item_id": "no-such-item", "quantity": 1}]}

    res = client.post("/api/orders", json=req, headers=auth(access_token))

    assert res.status_code == 404
    assert res.json()["error_code"] == "ERR_013"


def test_create_order_not_enough_stock(client: TestClient, access_token: str, items, db_session):
    req = {
        "items": [
            {"item_id": items["waffle"].id, "quantity": 1},   # 재고 충분
            {"item_id": items["choco"].id, "quantity": 100},  # 재고 부족
        ]
    }

    res = client.post("/api/orders", json=req, headers=auth(access_token))

    assert res.status_code == 409
    assert res.json()["error_code"] == "ERR_017"

    # 실패했으니 와플 재고도 그대로여야 함 (트랜잭션)
    db_session.refresh(items["waffle"])
    assert items["waffle"].stock == 5


def test_create_order_without_header(client: TestClient, items):
    req = {"items": [{"item_id": items["waffle"].id, "quantity": 1}]}

    res = client.post("/api/orders", json=req)

    assert res.status_code == 401
    assert res.json()["error_code"] == "ERR_005"


def test_create_order_invalid_token(client: TestClient, items):
    req = {"items": [{"item_id": items["waffle"].id, "quantity": 1}]}

    res = client.post("/api/orders", json=req, headers=auth("invalidtoken"))

    assert res.status_code == 401
    assert res.json()["error_code"] == "ERR_007"