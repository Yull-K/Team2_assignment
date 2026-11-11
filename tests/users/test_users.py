from fastapi.testclient import TestClient

from wapang.app.users.models import User

# TEST POST /api/users
def test_signup(
    client: TestClient
):
    req = {
        "email": "test1234@snu.ac.kr",
        "password": "password123"
    }

    res = client.post("/api/users", json=req)
    res_json = res.json()
    
    assert res.status_code == 201
    assert res_json["id"] is not None
    assert res_json["email"] == "test1234@snu.ac.kr"
    
    # 로그인 테스트
    res = client.post("/api/auth/tokens", json=req)
    res_json = res.json()
    
    assert res.status_code == 200

def test_signup_missing_email(
    client: TestClient
):
    req = {
        "password": "password123"
    }

    res = client.post("/api/users", json=req)
    res_json = res.json()
    
    assert res.status_code == 400
    assert res_json["error_code"] == "ERR_002"
    assert res_json["error_msg"] == "MISSING REQUIRED FIELDS"

def test_signup_missing_password(
    client: TestClient
):
    req = {
        "email": "test1234@snu.ac.kr"
    }

    res = client.post("/api/users", json=req)
    res_json = res.json()
    
    assert res.status_code == 400
    assert res_json["error_code"] == "ERR_002"
    assert res_json["error_msg"] == "MISSING REQUIRED FIELDS"

def test_signup_invalid_email(
    client: TestClient
):
    req = {
        "email": "test.snu.ac.kr",
        "password": "password123"
    }

    res = client.post("/api/users", json=req)
    res_json = res.json()
    
    assert res.status_code == 400
    assert res_json["error_code"] == "ERR_003"
    assert res_json["error_msg"] == "INVALID FIELD FORMAT"

def test_signup_short_password(
    client: TestClient
):
    req = {
        "email": "test1234@snu.ac.kr",
        "password": "short"
    }

    res = client.post("/api/users", json=req)
    res_json = res.json()
    
    assert res.status_code == 400
    assert res_json["error_code"] == "ERR_003"
    assert res_json["error_msg"] == "INVALID FIELD FORMAT"

def test_signup_long_password(
    client: TestClient
):
    req = {
        "email": "test1234@snu.ac.kr",
        "password": "longpasswordlongpassword"
    }

    res = client.post("/api/users", json=req)
    res_json = res.json()
    
    assert res.status_code == 400
    assert res_json["error_code"] == "ERR_003"
    assert res_json["error_msg"] == "INVALID FIELD FORMAT"


def test_signup_email_conflict(
    client: TestClient,
    user: User
):
    req = {
        "email": "test1234@snu.ac.kr",
        "password": "password321"
    }

    res = client.post("/api/users", json=req)
    res_json = res.json()

    assert res.status_code == 409
    assert res_json["error_code"] == "ERR_004"
    assert res_json["error_msg"] == "EMAIL ALREADY EXISTS"
    
# TEST GET /api/users/me
def test_get_me(
    client: TestClient,
    access_token: str
):
    auth_header = {"Authorization": f"Bearer {access_token}"}
    
    res = client.get("/api/users/me", headers=auth_header)
    
    assert res.status_code == 200
    
def test_get_me_without_header(
    client: TestClient
):
    res = client.get("/api/users/me")
    res_json = res.json()
    
    assert res.status_code == 401
    assert res_json["error_code"] == "ERR_005"
    assert res_json["error_msg"] == "UNAUTHENTICATED"
    
def test_get_me_invalid_header(
    client: TestClient,
    access_token: str
):
    invalid_header = {"Authorization": f"{access_token}"}
    
    res = client.get("/api/users/me", headers=invalid_header)
    res_json = res.json()
    
    assert res.status_code == 400
    assert res_json["error_code"] == "ERR_006"
    assert res_json["error_msg"] == "BAD AUTHORIZATION HEADER"
    
def test_get_me_invalid_token(
    client: TestClient,
):
    auth_header = {"Authorization": f"Bearer invalidtoken"}
    
    res = client.get("/api/users/me", headers=auth_header)
    res_json = res.json()
    
    assert res.status_code == 401
    assert res_json["error_code"] == "ERR_007"
    assert res_json["error_msg"] == "INVALID TOKEN"


# TEST PATCH /api/users/me
def test_update_me(
    client: TestClient,
    access_token: str
):
    auth_header = {"Authorization": f"Bearer {access_token}"}
    req = {
        "nickname": "와플이",
        "address": "서울시 관악구",
        "phone_number": "010-1234-5678"
    }

    res = client.patch("/api/users/me", json=req, headers=auth_header)
    res_json = res.json()

    assert res.status_code == 200
    assert res_json["nickname"] == "와플이"
    assert res_json["address"] == "서울시 관악구"
    assert res_json["phone_number"] == "010-1234-5678"
    assert res_json["email"] == "test1234@snu.ac.kr"

    # 진짜 저장됐는지 다시 조회
    res = client.get("/api/users/me", headers=auth_header)
    assert res.json()["nickname"] == "와플이"

def test_update_me_partial(
    client: TestClient,
    access_token: str
):
    auth_header = {"Authorization": f"Bearer {access_token}"}
    client.patch("/api/users/me", json={"nickname": "와플이"}, headers=auth_header)

    res = client.patch("/api/users/me", json={"address": "서울시 강남구"}, headers=auth_header)
    res_json = res.json()

    assert res.status_code == 200
    assert res_json["address"] == "서울시 강남구"
    assert res_json["nickname"] == "와플이"  # 안 보낸 값은 그대로

def test_update_me_empty_body(
    client: TestClient,
    access_token: str
):
    auth_header = {"Authorization": f"Bearer {access_token}"}

    res = client.patch("/api/users/me", json={}, headers=auth_header)
    res_json = res.json()

    assert res.status_code == 400
    assert res_json["error_code"] == "ERR_002"
    assert res_json["error_msg"] == "MISSING REQUIRED FIELDS"

def test_update_me_long_nickname(
    client: TestClient,
    access_token: str
):
    auth_header = {"Authorization": f"Bearer {access_token}"}

    res = client.patch("/api/users/me", json={"nickname": "a" * 21}, headers=auth_header)
    res_json = res.json()

    assert res.status_code == 400
    assert res_json["error_code"] == "ERR_003"
    assert res_json["error_msg"] == "INVALID FIELD FORMAT"

def test_update_me_long_address(
    client: TestClient,
    access_token: str
):
    auth_header = {"Authorization": f"Bearer {access_token}"}

    res = client.patch("/api/users/me", json={"address": "a" * 101}, headers=auth_header)
    res_json = res.json()

    assert res.status_code == 400
    assert res_json["error_code"] == "ERR_003"

def test_update_me_invalid_phone_number(
    client: TestClient,
    access_token: str
):
    auth_header = {"Authorization": f"Bearer {access_token}"}

    res = client.patch("/api/users/me", json={"phone_number": "01012345678"}, headers=auth_header)
    res_json = res.json()

    assert res.status_code == 400
    assert res_json["error_code"] == "ERR_003"

def test_update_me_without_header(
    client: TestClient
):
    res = client.patch("/api/users/me", json={"nickname": "와플이"})
    res_json = res.json()

    assert res.status_code == 401
    assert res_json["error_code"] == "ERR_005"

def test_update_me_invalid_header(
    client: TestClient,
    access_token: str
):
    invalid_header = {"Authorization": f"{access_token}"}

    res = client.patch("/api/users/me", json={"nickname": "와플이"}, headers=invalid_header)
    res_json = res.json()

    assert res.status_code == 400
    assert res_json["error_code"] == "ERR_006"

def test_update_me_invalid_token(
    client: TestClient
):
    auth_header = {"Authorization": "Bearer invalidtoken"}

    res = client.patch("/api/users/me", json={"nickname": "와플이"}, headers=auth_header)
    res_json = res.json()

    assert res.status_code == 401
    assert res_json["error_code"] == "ERR_007"