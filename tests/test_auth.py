from tests.conftest import TestClient

credentials_invalid = {
    "username": "Roman",
    "password": "a1!b2@c3#"
}

credentials_nonexistent_user = {
    "username": "Viktor",
    "password": "a1!b2@c3#"
}

credentials_correct = {
    "username": "Roman",
    "password": "a1#b2@c3!"
}

def test_generate_token_invalid_credentials(client: TestClient):
    response = client.post("/api/token", json=credentials_invalid)
    assert response.status_code == 401

def test_generate_token_nonexistent_user(client: TestClient):
    response = client.post("/api/token", json=credentials_nonexistent_user)
    assert response.status_code == 404

def test_generate_token_success(client: TestClient):
    response = client.post("/api/token", json=credentials_correct)
    assert response.status_code == 200

    # NOTE: /api/token returns a plain JWT string (not JSON)
    # therefore it has to be stripped of quotation marks
    token = response.text
    token = token.strip("\"")

    response_get = client.get("/api/messages", headers={"Authorization": f"Bearer {token}"})
    assert response_get.status_code == 200

def test_auth_invalid_credentials(client: TestClient):
    response = client.post("/api/auth", json=credentials_invalid)
    assert response.status_code == 401

def test_auth_nonexistent_user(client: TestClient):
    response = client.post("/api/auth", json=credentials_nonexistent_user)
    assert response.status_code == 404

def test_auth_success(client: TestClient):
    response = client.post("/api/auth", json=credentials_correct)
    assert response.status_code == 200

    # NOTE: /api/auth returns JSON: {"accessToken": "...", "user": {...}}
    # therefore we have to parse it with .json() and access the key directly
    token = response.json()["accessToken"]

    response_get = client.get("/api/messages", headers={"Authorization": f"Bearer {token}"})
    assert response_get.status_code == 200

def test_refresh_no_cookie(client: TestClient):
    response_refresh = client.post("/api/refresh")
    assert response_refresh.status_code == 401

def test_refresh_success(client: TestClient):
    # Step 1: Login via /api/auth (sets refresh_token cookie)
    response = client.post("/api/auth", json=credentials_correct)
    assert response.status_code == 200

    # Step 2: Verify refresh works with the cookie
    response_refresh = client.post("/api/refresh")
    assert response_refresh.status_code == 200

    data = response_refresh.json()
    assert "accessToken" in data

def test_logout_success(client: TestClient):
    # Step 1: Login via /api/auth (sets refresh_token cookie)
    response = client.post("/api/auth", json=credentials_correct)
    assert response.status_code == 200

    # Step 2: Verify refresh works with the cookie
    response_refresh = client.post("/api/refresh")
    assert response_refresh.status_code == 200

    # Step 3: Logout (deletes the cookie)
    response_logout = client.post("/api/logout")
    assert response_logout.status_code == 200

    # Step 4: Verify refresh no longer works (cookie was deleted)
    response_refresh_after = client.post("/api/refresh")
    assert response_refresh_after.status_code == 401
    