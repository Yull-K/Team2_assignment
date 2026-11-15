from fastapi.testclient import TestClient

from sqlalchemy.orm import Session
from wapang.app.items.models import Item

# 상점 테스트용 헬퍼 함수
def create_auth_header(client: TestClient, email: str, password: str = "password123") -> dict:
    client.post("/api/users", json={"email": email, "password": password})
    res = client.post("/api/auth/tokens", json={"email": email, "password": password})
    return {"Authorization": f"Bearer {res.json()['access_token']}"}

# POST REQUEST 
def store_req(**overrides) -> dict:
    req = {
        "store_name": "store1",
        "address": "address1",
        "email": "fastapi@wafflestudio.com",
        "phone_number": "010-1234-5678",
        "delivery_fee": 3000,
    }
    req.update(overrides)
    return req

# TEST POST /api/stores
def test_add_store(
    client: TestClient,
    access_token: str,
):
    auth_header = {"Authorization": f"Bearer {access_token}"}

    request = store_req()

    response = client.post("/api/stores", json=request, headers=auth_header)
    assert response.status_code == 201

    res_json = response.json()
    assert res_json["id"] is not None
    assert res_json["store_name"] == "store1"
    assert res_json["address"] == "address1"
    assert res_json["email"] == "fastapi@wafflestudio.com"
    assert res_json["phone_number"] == "010-1234-5678"
    assert res_json["delivery_fee"] == 3000

# 요청 필드가 비어있는 경우	| 400 | ERR_002 | MISSING REQUIRED FIELDS
def test_add_missing_store_name(
    client: TestClient,
    access_token: str,
):
    auth_header = {"Authorization": f"Bearer {access_token}"}
    request = store_req()
    request.pop("store_name")

    res = client.post("/api/stores", json=request, headers=auth_header)
    res_json = res.json()
    
    assert res.status_code == 400
    assert res_json["error_code"] == "ERR_002"
    assert res_json["error_msg"] == "MISSING REQUIRED FIELDS"

def test_add_missing_address(
    client: TestClient,
    access_token: str,
):
    auth_header = {"Authorization": f"Bearer {access_token}"}
    request = store_req()
    request.pop("address")

    res = client.post("/api/stores", json=request, headers=auth_header)
    res_json = res.json()
    
    assert res.status_code == 400
    assert res_json["error_code"] == "ERR_002"
    assert res_json["error_msg"] == "MISSING REQUIRED FIELDS"

def test_add_missing_email(
    client: TestClient,
    access_token: str,
):
    auth_header = {"Authorization": f"Bearer {access_token}"}
    request = store_req()
    request.pop("email")

    res = client.post("/api/stores", json=request, headers=auth_header)
    res_json = res.json()
    
    assert res.status_code == 400
    assert res_json["error_code"] == "ERR_002"
    assert res_json["error_msg"] == "MISSING REQUIRED FIELDS"

def test_add_missing_phone_number(
    client: TestClient,
    access_token: str,
):
    auth_header = {"Authorization": f"Bearer {access_token}"}
    request = store_req()
    request.pop("phone_number")

    res = client.post("/api/stores", json=request, headers=auth_header)
    res_json = res.json()
    
    assert res.status_code == 400
    assert res_json["error_code"] == "ERR_002"
    assert res_json["error_msg"] == "MISSING REQUIRED FIELDS"

def test_add_missing_delivery_fee(
    client: TestClient,
    access_token: str,
):
    auth_header = {"Authorization": f"Bearer {access_token}"}
    request = store_req()
    request.pop("delivery_fee")

    res = client.post("/api/stores", json=request, headers=auth_header)
    res_json = res.json()
    
    assert res.status_code == 400
    assert res_json["error_code"] == "ERR_002"
    assert res_json["error_msg"] == "MISSING REQUIRED FIELDS"

# 요청 필드의 형식이 올바르지 않은 경우	| 400 | ERR_003 | INVALID FIELD FORMAT
def test_add_short_store_name(
    client: TestClient,
    access_token: str,
): 
    auth_header = {"Authorization": f"Bearer {access_token}"}
    request = store_req(store_name="sr")

    res = client.post("/api/stores", json=request, headers=auth_header)
    res_json = res.json()

    assert res.status_code == 400
    assert res_json["error_code"] == "ERR_003"
    assert res_json["error_msg"] == "INVALID FIELD FORMAT"

def test_add_long_store_name(
    client: TestClient,
    access_token: str,
): 
    auth_header = {"Authorization": f"Bearer {access_token}"}
    request = store_req(store_name="longstorenamelongstorename")

    res = client.post("/api/stores", json=request, headers=auth_header)
    res_json = res.json()

    assert res.status_code == 400
    assert res_json["error_code"] == "ERR_003"
    assert res_json["error_msg"] == "INVALID FIELD FORMAT"

def test_add_long_address(
    client: TestClient,
    access_token: str,
): 
    auth_header = {"Authorization": f"Bearer {access_token}"}
    request = store_req(address="longaddresslongaddresslongaddresslongaddresslongaddresslongaddresslongaddresslongaddresslongaddresslongaddress")

    res = client.post("/api/stores", json=request, headers=auth_header)
    res_json = res.json()

    assert res.status_code == 400
    assert res_json["error_code"] == "ERR_003"
    assert res_json["error_msg"] == "INVALID FIELD FORMAT"

def test_add_invalid_email(
    client: TestClient,
    access_token: str,
): 
    auth_header = {"Authorization": f"Bearer {access_token}"}
    request = store_req(email="email")

    res = client.post("/api/stores", json=request, headers=auth_header)
    res_json = res.json()

    assert res.status_code == 400
    assert res_json["error_code"] == "ERR_003"
    assert res_json["error_msg"] == "INVALID FIELD FORMAT"

def test_add_invalid_phone_number(
    client: TestClient,
    access_token: str,
): 
    auth_header = {"Authorization": f"Bearer {access_token}"}
    request = store_req(phone_number="000")

    res = client.post("/api/stores", json=request, headers=auth_header)
    res_json = res.json()

    assert res.status_code == 400
    assert res_json["error_code"] == "ERR_003"
    assert res_json["error_msg"] == "INVALID FIELD FORMAT"

def test_add_invalid_delivery_fee(
    client: TestClient,
    access_token: str,
): 
    auth_header = {"Authorization": f"Bearer {access_token}"}
    request = store_req(delivery_fee=-1)

    res = client.post("/api/stores", json=request, headers=auth_header)
    res_json = res.json()

    assert res.status_code == 400
    assert res_json["error_code"] == "ERR_003"
    assert res_json["error_msg"] == "INVALID FIELD FORMAT"

# Authorization 헤더가 제시되지 않은 경우 | 401 | ERR_005 | UNAUTHENTICATED
def test_add_without_header(
    client: TestClient,
): 
    request = store_req()

    res = client.post("/api/stores", json=request)
    res_json = res.json()

    assert res.status_code == 401
    assert res_json["error_code"] == "ERR_005"
    assert res_json["error_msg"] == "UNAUTHENTICATED"

# Authorization 헤더 값의 형식이 비정상적인 경우 | 400 | ERR_006 | BAD AUTHORIZATION HEADER
def test_add_invalid_header(
    client: TestClient,
    access_token: str,
):
    auth_header = {"Authorization": f"{access_token}"}
    request = store_req()

    res = client.post("/api/stores", json=request, headers=auth_header)
    res_json = res.json()

    assert res.status_code == 400
    assert res_json["error_code"] == "ERR_006"
    assert res_json["error_msg"] == "BAD AUTHORIZATION HEADER"

# 토큰이 유효하지 않은 경우	| 401 | ERR_007 | INVALID TOKEN
def test_add_invalid_token(
    client: TestClient,
):
    auth_header = {"Authorization": "Bearer invalidtoken"}
    request = store_req()

    res = client.post("/api/stores", json=request, headers=auth_header)
    res_json = res.json()

    assert res.status_code == 401
    assert res_json["error_code"] == "ERR_007"
    assert res_json["error_msg"] == "INVALID TOKEN"

# 이미 상점을 소유하고 있는 경우 | 409 | ERR_008 | STORE ALREADY EXISTS
def test_add_store_already_exists(
    client: TestClient,
    access_token: str,
):
    auth_header = {"Authorization": f"Bearer {access_token}"}

    # 먼저 중복되도록 상점을 하나 생성
    client.post("/api/stores", json=store_req(), headers=auth_header)
    
    # 같은 유저로 다른 상점을 또 생성 시도
    second_req = store_req(
        store_name="store2",
        email="store2@wafflestudio.com",
        phone_number="010-9999-9999",
    )

    res = client.post("/api/stores", json=second_req, headers=auth_header)
    res_json = res.json()

    assert res.status_code == 409
    assert res_json["error_code"] == "ERR_008"
    assert res_json["error_msg"] == "STORE ALREADY EXISTS"
    
# 상점명/이메일/전화번호가 중복되는 경우 | 409 | ERR_009 | STORE INFO CONFLICT
def test_add_store_conflict_name(client: TestClient, access_token: str):
    # 1번 유저가 먼저 상점 생성
    auth1 = {"Authorization": f"Bearer {access_token}"}
    client.post("/api/stores", json=store_req(), headers=auth1)

    # 2번 유저가 같은 store_name("store1")으로 생성 시도
    auth2 = create_auth_header(client, "other@snu.ac.kr")
    conflict_req = store_req(
        email="other_store@wafflestudio.com",
        phone_number="010-9999-9999",
    )
    res = client.post("/api/stores", json=conflict_req, headers=auth2)
    res_json = res.json()

    assert res.status_code == 409
    assert res_json["error_code"] == "ERR_009"
    assert res_json["error_msg"] == "STORE INFO CONFLICT"

def test_add_store_conflict_email(client: TestClient, access_token: str):
    # 1번 유저가 먼저 상점 생성
    auth1 = {"Authorization": f"Bearer {access_token}"}
    client.post("/api/stores", json=store_req(), headers=auth1)

    # 2번 유저가 같은 store_name("store1")으로 생성 시도
    auth2 = create_auth_header(client, "other@snu.ac.kr")
    conflict_req = store_req(
        store="store2",
        phone_number="010-9999-9999",
    )
    res = client.post("/api/stores", json=conflict_req, headers=auth2)
    res_json = res.json()

    assert res.status_code == 409
    assert res_json["error_code"] == "ERR_009"
    assert res_json["error_msg"] == "STORE INFO CONFLICT"

def test_add_store_conflict_phone_number(client: TestClient, access_token: str):
    # 1번 유저가 먼저 상점 생성
    auth1 = {"Authorization": f"Bearer {access_token}"}
    client.post("/api/stores", json=store_req(), headers=auth1)

    # 2번 유저가 같은 store_name("store1")으로 생성 시도
    auth2 = create_auth_header(client, "other@snu.ac.kr")
    conflict_req = store_req(
        store_name="store2",
        email="other_store@wafflestudio.com",
    )
    res = client.post("/api/stores", json=conflict_req, headers=auth2)
    res_json = res.json()

    assert res.status_code == 409
    assert res_json["error_code"] == "ERR_009"
    assert res_json["error_msg"] == "STORE INFO CONFLICT"

# TEST PATCH /api/stores/{store_id}
def test_update_store(
    client: TestClient,
    access_token: str,
): 
    auth = {"Authorization": f"Bearer {access_token}"}
    create = client.post("/api/stores", json=store_req(), headers=auth)
    store_id = create.json()["id"]

    test_req = {
        "store_name": "update_store",
        "address": "update_address",
        "email": "update_fastapi@wafflestudio.com",
        "phone_number": "010-1234-5679",
        "delivery_fee": 5000,
    }
    res = client.patch(f"/api/stores/{store_id}", json=test_req, headers=auth)
    assert res.status_code == 200

    res_json = res.json()
    assert res_json["id"] is not None
    assert res_json["store_name"] == "update_store"
    assert res_json["address"] == "update_address"
    assert res_json["email"] == "update_fastapi@wafflestudio.com"
    assert res_json["phone_number"] == "010-1234-5679"
    assert res_json["delivery_fee"] == 5000

    # partial update test
    partial_req = {"store_name":"update_store1"}
    partial_res = client.patch(f"/api/stores/{store_id}", json=partial_req, headers=auth)
    assert partial_res.status_code == 200

    partial_json = partial_res.json()
    assert partial_json["store_name"] == "update_store1"

    partial_req = {"address":"update_address1"}
    partial_res = client.patch(f"/api/stores/{store_id}", json=partial_req, headers=auth)
    assert partial_res.status_code == 200

    partial_json = partial_res.json()
    assert partial_json["address"] == "update_address1"

    partial_req = {"email":"update1_fastapi@wafflestudio.com"}
    partial_res = client.patch(f"/api/stores/{store_id}", json=partial_req, headers=auth)
    assert partial_res.status_code == 200

    partial_json = partial_res.json()
    assert partial_json["email"] == "update1_fastapi@wafflestudio.com"

    partial_req = {"phone_number":"010-1234-5677"}
    partial_res = client.patch(f"/api/stores/{store_id}", json=partial_req, headers=auth)
    assert partial_res.status_code == 200

    partial_json = partial_res.json()
    assert partial_json["phone_number"] == "010-1234-5677"

    partial_req = {"delivery_fee":6000}
    partial_res = client.patch(f"/api/stores/{store_id}", json=partial_req, headers=auth)
    assert partial_res.status_code == 200

    partial_json = partial_res.json()
    assert partial_json["delivery_fee"] == 6000

# 요청 필드가 비어있는 경우	| 400 | ERR_002	| MISSING REQUIRED FIELDS
def test_update_store_empty_body(
    client: TestClient,
    access_token: str,
):
    auth = {"Authorization": f"Bearer {access_token}"}
    create = client.post("/api/stores", json=store_req(), headers=auth)
    store_id = create.json()["id"]

    res = client.patch(f"/api/stores/{store_id}", json={}, headers=auth)
    res_json = res.json()
    assert res.status_code == 400
    assert res_json["error_code"] == "ERR_002"
    assert res_json["error_msg"] == "MISSING REQUIRED FIELDS"

# 요청 필드의 형식이 올바르지 않은 경우	| 400 | ERR_003 | INVALID FIELD FORMAT
def test_update_short_store_name(
    client: TestClient,
    access_token: str,
): 
    auth = {"Authorization": f"Bearer {access_token}"}
    create = client.post("/api/stores", json=store_req(), headers=auth)
    store_id = create.json()["id"]

    req = {"store_name":"sr"}

    res = client.patch(f"/api/stores/{store_id}", json=req, headers=auth)
    res_json = res.json()

    assert res.status_code == 400
    assert res_json["error_code"] == "ERR_003"
    assert res_json["error_msg"] == "INVALID FIELD FORMAT"

def test_update_long_store_name(
    client: TestClient,
    access_token: str,
): 
    auth = {"Authorization": f"Bearer {access_token}"}
    create = client.post("/api/stores", json=store_req(), headers=auth)
    store_id = create.json()["id"]

    req = {"store_name":"longstorenamelongstorename"}

    res = client.patch(f"/api/stores/{store_id}", json=req, headers=auth)
    res_json = res.json()

    assert res.status_code == 400
    assert res_json["error_code"] == "ERR_003"
    assert res_json["error_msg"] == "INVALID FIELD FORMAT"

def test_update_long_address(
    client: TestClient,
    access_token: str,
): 
    auth = {"Authorization": f"Bearer {access_token}"}
    create = client.post("/api/stores", json=store_req(), headers=auth)
    store_id = create.json()["id"]

    req = {"address":"longaddresslongaddresslongaddresslongaddresslongaddresslongaddresslongaddresslongaddresslongaddresslongaddress"}

    res = client.patch(f"/api/stores/{store_id}", json=req, headers=auth)
    res_json = res.json()

    assert res.status_code == 400
    assert res_json["error_code"] == "ERR_003"
    assert res_json["error_msg"] == "INVALID FIELD FORMAT"

def test_update_invalid_email(
    client: TestClient,
    access_token: str,
): 
    auth = {"Authorization": f"Bearer {access_token}"}
    create = client.post("/api/stores", json=store_req(), headers=auth)
    store_id = create.json()["id"]

    req = {"email":"fastapi"}

    res = client.patch(f"/api/stores/{store_id}", json=req, headers=auth)
    res_json = res.json()

    assert res.status_code == 400
    assert res_json["error_code"] == "ERR_003"
    assert res_json["error_msg"] == "INVALID FIELD FORMAT"

def test_update_invalid_phone_number(
    client: TestClient,
    access_token: str,
): 
    auth = {"Authorization": f"Bearer {access_token}"}
    create = client.post("/api/stores", json=store_req(), headers=auth)
    store_id = create.json()["id"]

    req = {"phone_number":"010"}

    res = client.patch(f"/api/stores/{store_id}", json=req, headers=auth)
    res_json = res.json()

    assert res.status_code == 400
    assert res_json["error_code"] == "ERR_003"
    assert res_json["error_msg"] == "INVALID FIELD FORMAT"

def test_update_invalid_delivery_fee(
    client: TestClient,
    access_token: str,
): 
    auth = {"Authorization": f"Bearer {access_token}"}
    create = client.post("/api/stores", json=store_req(), headers=auth)
    store_id = create.json()["id"]

    req = {"delivery_fee":-1}

    res = client.patch(f"/api/stores/{store_id}", json=req, headers=auth)
    res_json = res.json()

    assert res.status_code == 400
    assert res_json["error_code"] == "ERR_003"
    assert res_json["error_msg"] == "INVALID FIELD FORMAT"

# Authorization 헤더가 제시되지 않은 경우 | 401 | ERR_005 | UNAUTHENTICATED
def test_update_without_header(
    client: TestClient,
    access_token: str,
): 
    auth = {"Authorization": f"Bearer {access_token}"}
    create = client.post("/api/stores", json=store_req(), headers=auth)
    store_id = create.json()["id"]

    res = client.patch(f"/api/stores/{store_id}", json={"store_name":"store"})
    res_json = res.json()

    assert res.status_code == 401
    assert res_json["error_code"] == "ERR_005"
    assert res_json["error_msg"] == "UNAUTHENTICATED"

# Authorization 헤더 값의 형식이 비정상적인 경우 | 400 | ERR_006 | BAD AUTHORIZATION HEADER
def test_update_invalid_header(
    client: TestClient,
    access_token: str,
):
    auth_header = {"Authorization": f"{access_token}"}
    request = store_req()

    res = client.patch("/api/stores/some-id", json=request, headers=auth_header)
    res_json = res.json()

    assert res.status_code == 400
    assert res_json["error_code"] == "ERR_006"
    assert res_json["error_msg"] == "BAD AUTHORIZATION HEADER"

# 토큰이 유효하지 않은 경우	| 401 | ERR_007 | INVALID TOKEN
def test_update_invalid_token(
    client: TestClient,
):
    auth_header = {"Authorization": "Bearer invalidtoken"}
    request = store_req()

    res = client.patch("/api/stores/some-id", json=request, headers=auth_header)
    res_json = res.json()

    assert res.status_code == 401
    assert res_json["error_code"] == "ERR_007"
    assert res_json["error_msg"] == "INVALID TOKEN"

# 상점명/이메일/전화번호가 중복되는 경우 | 409 | ERR_009 | STORE INFO CONFLICT
def test_update_store_conflict_name(client: TestClient, access_token: str):
    # 1번 유저가 먼저 상점 생성
    auth1 = {"Authorization": f"Bearer {access_token}"}
    client.post("/api/stores", json=store_req(), headers=auth1)

    # 2번 유저가 같은 store_name("store1")으로 수정 시도
    auth2 = create_auth_header(client, "other@snu.ac.kr")
    req = {
        "store_name": "store2",
        "address": "address2",
        "email": "fastapi2@wafflestudio.com",
        "phone_number": "010-1234-5679",
        "delivery_fee": 4000,
    }
    create = client.post("/api/stores", json=req, headers=auth2)
    store_id = create.json()["id"]

    res = client.patch(f"/api/stores/{store_id}", json={"store_name":"store1"}, headers=auth2)
    res_json = res.json()

    assert res.status_code == 409
    assert res_json["error_code"] == "ERR_009"
    assert res_json["error_msg"] == "STORE INFO CONFLICT"

def test_update_store_conflict_email(client: TestClient, access_token: str):
    # 1번 유저가 먼저 상점 생성
    auth1 = {"Authorization": f"Bearer {access_token}"}
    client.post("/api/stores", json=store_req(), headers=auth1)

    # 2번 유저가 같은 store_name("store1")으로 수정 시도
    auth2 = create_auth_header(client, "other@snu.ac.kr")
    req = {
        "store_name": "store2",
        "address": "address2",
        "email": "fastapi2@wafflestudio.com",
        "phone_number": "010-1234-5679",
        "delivery_fee": 4000,
    }
    create = client.post("/api/stores", json=req, headers=auth2)
    store_id = create.json()["id"]

    res = client.patch(f"/api/stores/{store_id}", json={"email":"fastapi@wafflestudio.com"}, headers=auth2)
    res_json = res.json()

    assert res.status_code == 409
    assert res_json["error_code"] == "ERR_009"
    assert res_json["error_msg"] == "STORE INFO CONFLICT"

def test_update_store_conflict_phone_number(client: TestClient, access_token: str):
    # 1번 유저가 먼저 상점 생성
    auth1 = {"Authorization": f"Bearer {access_token}"}
    client.post("/api/stores", json=store_req(), headers=auth1)

    # 2번 유저가 같은 store_name("store1")으로 수정 시도
    auth2 = create_auth_header(client, "other@snu.ac.kr")
    req = {
        "store_name": "store2",
        "address": "address2",
        "email": "fastapi2@wafflestudio.com",
        "phone_number": "010-1234-5679",
        "delivery_fee": 4000,
    }
    create = client.post("/api/stores", json=req, headers=auth2)
    store_id = create.json()["id"]

    res = client.patch(f"/api/stores/{store_id}", json={"phone_number":"010-1234-5678"}, headers=auth2)
    res_json = res.json()

    assert res.status_code == 409
    assert res_json["error_code"] == "ERR_009"
    assert res_json["error_msg"] == "STORE INFO CONFLICT"

# 상점이 존재하지 않는 경우 | 404 | ERR_010 | STORE NOT FOUND
def test_update_no_store_exist(
    client: TestClient,
    access_token: str,      
): 
    auth = {"Authorization": f"Bearer {access_token}"}
    client.post("/api/stores", json=store_req(), headers=auth)

    res = client.patch(f"/api/stores/1111", json={"store_name":"store"}, headers=auth)
    res_json = res.json()

    assert res.status_code == 404
    assert res_json["error_code"] == "ERR_010"
    assert res_json["error_msg"] == "STORE NOT FOUND"

# 상점을 소유하지 않은 경우	| 403 | ERR_011 | NO STORE OWNED
def test_update_no_store_exist(
    client: TestClient,
    access_token: str,      
): 
    auth = {"Authorization": f"Bearer {access_token}"}

    res = client.patch(f"/api/stores/1", json={"store_name":"store"}, headers=auth)
    res_json = res.json()

    assert res.status_code == 403
    assert res_json["error_code"] == "ERR_011"
    assert res_json["error_msg"] == "NO STORE OWNED"

# 다른 상점을 수정하려는 경우 | 403 | ERR_012 | NOT YOUR STORE
def test_update_no_store_exist(
    client: TestClient,
    access_token: str,      
): 
    auth1 = {"Authorization": f"Bearer {access_token}"}
    create = client.post("/api/stores", json=store_req(), headers=auth1)
    store_id = create.json()["id"]

    test_req = {
        "store_name": "update_store",
        "address": "update_address",
        "email": "update_fastapi@wafflestudio.com",
        "phone_number": "010-1234-5679",
        "delivery_fee": 5000,
    }

    auth2 = create_auth_header(client, "other@snu.ac.kr")
    client.post("/api/stores", json=test_req, headers=auth2)

    res = client.patch(f"/api/stores/{store_id}", json={"store_name":"store"}, headers=auth2)
    res_json = res.json()

    assert res.status_code == 403
    assert res_json["error_code"] == "ERR_012"
    assert res_json["error_msg"] == "NOT YOUR STORE"

# TEST GET /api/stores/{store_id}
def test_get_store(
    client: TestClient,
    access_token: str, 
):
    auth_header = {"Authorization": f"Bearer {access_token}"}
    create = client.post("/api/stores", json=store_req(), headers=auth_header)
    store_id = create.json()["id"]

    res = client.get(f"/api/stores/{store_id}")
    assert res.status_code == 200

    res_json = res.json()
    assert res_json["id"] is not None
    assert res_json["store_name"] == "store1"
    assert res_json["address"] == "address1"
    assert res_json["email"] == "fastapi@wafflestudio.com"
    assert res_json["phone_number"] == "010-1234-5678"
    assert res_json["delivery_fee"] == 3000

# 상점이 존재하지 않는 경우 | 404 | ERR_010 | STORE NOT FOUND
def test_get_no_store_exist(
    client: TestClient,  
): 
    res = client.get(f"/api/stores/1111")
    res_json = res.json()

    assert res.status_code == 404
    assert res_json["error_code"] == "ERR_010"
    assert res_json["error_msg"] == "STORE NOT FOUND"

# TEST GET /api/stores/{store_id}/items
def test_get_items(
    client: TestClient,
    access_token: str, 
    db_session: Session,
):
    auth_header = {"Authorization": f"Bearer {access_token}"}
    create = client.post("/api/stores", json=store_req(), headers=auth_header)
    store_id = create.json()["id"]

    item1 = Item(store_id = store_id, name="와플", price = 10000, stock =15)
    item2 = Item(store_id = store_id, name="시럽", price = 3000, stock =8)
    db_session.add_all([item1, item2])
    db_session.commit()

    res = client.get(f"/api/stores/{store_id}/items")
    assert res.status_code == 200

    res_json = res.json()
    assert len(res_json) == 2
    assert res_json[0]["item_name"] == "와플"
    assert res_json[0]["price"] == 10000
    assert res_json[0]["stock"] == 15

def test_get_items_empty(
    client: TestClient,
    access_token: str,
):
    auth_header = {"Authorization": f"Bearer {access_token}"}
    create = client.post("/api/stores", json=store_req(), headers=auth_header)
    store_id = create.json()["id"]
    res = client.get(f"/api/stores/{store_id}/items")
    assert res.status_code == 200
    assert res.json() == []

# 상점이 존재하지 않는 경우	| 404 | ERR_010 | STORE NOT FOUND
def test_get_items_store_not_found(
    client: TestClient,
):
    res = client.get("/api/stores/1111/items")
    res_json = res.json()
    assert res.status_code == 404
    assert res_json["error_code"] == "ERR_010"
    assert res_json["error_msg"] == "STORE NOT FOUND"