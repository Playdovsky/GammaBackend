from tests.conftest import TestClient

payload = {
    "username": "Roman",
    "password": "a1#b2@c3!"
}

contact_payload = {
    "name": "Richard",
    "email": "rich_richard@gmail.com",
    "message": "I like your project, can you tell me more about it?"
}

def get_token(client: TestClient):
    token_response = client.post("/api/token", json=payload)
    token = token_response.text
    token = token.strip("\"")
    return token

def test_get_messages_no_token(client: TestClient):
    client.post("/api/contact", json=contact_payload)

    response = client.get("/api/messages")
    assert response.status_code == 401

def test_get_messages_success(client: TestClient):
    client.post("/api/contact", json=contact_payload)
    token = get_token(client)

    response = client.get("/api/messages", headers={"Authorization": f"Bearer {token}"})
    data = response.json()
    assert response.status_code == 200
    assert data[0]["name"] == "Richard"
    assert data[0]["email"] == "rich_richard@gmail.com"
    assert data[0]["message"] == "I like your project, can you tell me more about it?"
    assert data[0]["archived"] == False

def test_archive_message_no_token(client: TestClient):
    client.post("/api/contact", json=contact_payload)

    response_archive = client.patch("/api/messages/1")
    assert response_archive.status_code == 401

def test_archive_message_success(client: TestClient):
    client.post("/api/contact", json=contact_payload)
    token = get_token(client)

    response_archive = client.patch("/api/messages/1", headers={"Authorization": f"Bearer {token}"})
    assert response_archive.status_code == 200

    response = client.get("/api/messages", headers={"Authorization": f"Bearer {token}"})
    data = response.json()
    assert data == []

def test_archive_archived_message(client: TestClient):
    client.post("/api/contact", json=contact_payload)
    token = get_token(client)

    response_archive = client.patch("/api/messages/1", headers={"Authorization": f"Bearer {token}"})
    assert response_archive.status_code == 200

    response_archive = client.patch("/api/messages/1", headers={"Authorization": f"Bearer {token}"})
    assert response_archive.status_code == 409

def test_archive_nonexistent_message(client: TestClient):
    client.post("/api/contact", json=contact_payload)
    token = get_token(client)

    response_archive = client.patch("/api/messages/2", headers={"Authorization": f"Bearer {token}"})
    assert response_archive.status_code == 404

def test_delete_message_no_token(client: TestClient):
    client.post("/api/contact", json=contact_payload)
    
    response_delete = client.delete("/api/messages/1")
    assert response_delete.status_code == 401

def test_delete_message_success(client: TestClient):
    client.post("/api/contact", json=contact_payload)
    token = get_token(client)
    
    response_delete = client.delete("/api/messages/1", headers={"Authorization": f"Bearer {token}"})
    assert response_delete.status_code == 200

    response = client.get("/api/messages", headers={"Authorization": f"Bearer {token}"})
    data = response.json()
    assert data == []

def test_delete_nonexistent_message(client: TestClient):
    client.post("/api/contact", json=contact_payload)
    token = get_token(client)
    
    response_delete = client.delete("/api/messages/2", headers={"Authorization": f"Bearer {token}"})
    assert response_delete.status_code == 404