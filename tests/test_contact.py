from tests.conftest import TestClient

payload = {
    "name": "Matthew",
    "email": "matthew.stick@gmail.com",
    "message": "This is a test message"
}

payload2 = {
    "name": "Matthew",
    "email": "matthew.stickgmail.com",
    "message": "This is a test message"
}

payload3 = {
    "name": "Carlos",
    "email": "carlos_fontanciones@gmail",
    "message": "This is a test message"
}

payload4 = {
    "name": "Carlos",
    "email": "carlos_fontanciones@gmail",
}

payload5 = {
    "name": "                          ",
    "email": "carlos_fontanciones@gmail",
    "message": "This is a test message"
}

def test_contact_success(client: TestClient):
    response = client.post("/api/contact", json=payload)
    data = response.json()

    assert response.status_code == 200
    assert data["name"] == "Matthew"
    assert data["email"] == "matthew.stick@gmail.com"
    assert data["message"] == "This is a test message"
    assert data["archived"] == False

def test_contact_fail(client: TestClient):
    response = client.post("/api/contact", json=payload2)
    assert response.status_code == 400

def test_contact_fail2(client: TestClient):
    response = client.post("/api/contact", json=payload3)
    assert response.status_code == 400
    
def test_contact_fail3(client: TestClient):
    response = client.post("/api/contact", json=payload4)
    assert response.status_code == 422

def test_contact_fail4(client: TestClient):
    response = client.post("/api/contact", json=payload5)
    assert response.status_code == 400