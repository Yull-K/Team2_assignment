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
    



# ---------- 준비: 주문 1개 + 다른 유저 토큰 ----------
@pytest.fixture
def order_id(client: TestClient, access_token: str, items) -> str:
    req = {
        "items": [
            {"item_id": items["waffle"].id, "quantity": 2},
            {"item_id": items["choco"].id, "quantity": 1},
        ]
    }
    res = client.post("/api/orders", json=req, headers=auth(access_token))
    return res.json()["order_id"]


@pytest.fixture
def other_access_token(client: TestClient) -> str:
    req = {"email": "other@snu.ac.kr", "password": "password123"}
    client.post("/api/users", json=req)
    res = client.post("/api/auth/tokens", json=req)
    return res.json()["access_token"]


# ---------- TEST GET /api/orders/{order_id} ----------
def test_get_order(client: TestClient, access_token: str, order_id: str):
    res = client.get(f"/api/orders/{order_id}", headers=auth(access_token))
    res_json = res.json()

    assert res.status_code == 200
    assert res_json["order_id"] == order_id
    assert res_json["total_price"] == 40500
    assert len(res_json["details"]) == 2
    assert res_json["status"] == "ORDERED"


def test_get_order_not_found(client: TestClient, access_token: str):
    res = client.get("/api/orders/no-such-order", headers=auth(access_token))

    assert res.status_code == 404
    assert res.json()["error_code"] == "ERR_019"


def test_get_order_not_your_order(client: TestClient, order_id: str, other_access_token: str):
    res = client.get(f"/api/orders/{order_id}", headers=auth(other_access_token))

    assert res.status_code == 403
    assert res.json()["error_code"] == "ERR_020"


def test_get_order_without_header(client: TestClient, order_id: str):
    res = client.get(f"/api/orders/{order_id}")

    assert res.status_code == 401
    assert res.json()["error_code"] == "ERR_005"


# ---------- TEST PATCH /api/orders/{order_id} ----------
def test_cancel_order(client: TestClient, access_token: str, order_id: str):
    res = client.patch(
        f"/api/orders/{order_id}", json={"status": "CANCELED"}, headers=auth(access_token)
    )

    assert res.status_code == 204
    assert res.content == b""  # 본문 없음

    # 진짜 바뀌었는지 다시 조회
    res = client.get(f"/api/orders/{order_id}", headers=auth(access_token))
    assert res.json()["status"] == "CANCELED"


def test_complete_order(client: TestClient, access_token: str, order_id: str):
    res = client.patch(
        f"/api/orders/{order_id}", json={"status": "COMPLETE"}, headers=auth(access_token)
    )

    assert res.status_code == 204

    res = client.get(f"/api/orders/{order_id}", headers=auth(access_token))
    assert res.json()["status"] == "COMPLETE"


def test_update_order_already_canceled(client: TestClient, access_token: str, order_id: str):
    client.patch(
        f"/api/orders/{order_id}", json={"status": "CANCELED"}, headers=auth(access_token)
    )

    res = client.patch(
        f"/api/orders/{order_id}", json={"status": "COMPLETE"}, headers=auth(access_token)
    )

    assert res.status_code == 409
    assert res.json()["error_code"] == "ERR_021"


def test_update_order_invalid_status(client: TestClient, access_token: str, order_id: str):
    res = client.patch(
        f"/api/orders/{order_id}", json={"status": "ORDERED"}, headers=auth(access_token)
    )

    assert res.status_code == 400
    assert res.json()["error_code"] == "ERR_003"


def test_update_order_missing_status(client: TestClient, access_token: str, order_id: str):
    res = client.patch(f"/api/orders/{order_id}", json={}, headers=auth(access_token))

    assert res.status_code == 400
    assert res.json()["error_code"] == "ERR_002"


def test_update_order_not_found(client: TestClient, access_token: str):
    res = client.patch(
        "/api/orders/no-such-order", json={"status": "CANCELED"}, headers=auth(access_token)
    )

    assert res.status_code == 404
    assert res.json()["error_code"] == "ERR_019"


def test_update_order_not_your_order(client: TestClient, order_id: str, other_access_token: str):
    res = client.patch(
        f"/api/orders/{order_id}", json={"status": "CANCELED"}, headers=auth(other_access_token)
    )

    assert res.status_code == 403
    assert res.json()["error_code"] == "ERR_020"


def test_update_order_without_header(client: TestClient, order_id: str):
    res = client.patch(f"/api/orders/{order_id}", json={"status": "CANCELED"})

    assert res.status_code == 401
    assert res.json()["error_code"] == "ERR_005"