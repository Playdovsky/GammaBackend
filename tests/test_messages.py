from tests.conftest import TestClient, Session
from models import ContactMessage
from sqlmodel import select

credentials = {
    "username": "Roman",
    "password": "a1#b2@c3!"
}

contact_credentials = {
    "name": "Richard",
    "email": "rich_richard@gmail.com",
    "message": "I like your project, can you tell me more about it?"
}

def get_token(client: TestClient):
    # NOTE: /api/token returns a plain JWT string (not JSON)
    # therefore it has to be stripped of quotation marks
    token_response = client.post("/api/token", json=credentials)
    token = token_response.text
    token = token.strip("\"")
    return token

def test_get_messages_no_token(client: TestClient):
    client.post("/api/contact", json=contact_credentials)

    response = client.get("/api/messages")
    assert response.status_code == 401

def test_get_messages_success(client: TestClient):
    client.post("/api/contact", json=contact_credentials)
    token = get_token(client)

    response = client.get("/api/messages", headers={"Authorization": f"Bearer {token}"})
    data = response.json()
    assert response.status_code == 200
    assert data[0]["name"] == "Richard"
    assert data[0]["email"] == "rich_richard@gmail.com"
    assert data[0]["message"] == "I like your project, can you tell me more about it?"
    assert data[0]["archived"] == False

def test_archive_message_no_token(client: TestClient):
    client.post("/api/contact", json=contact_credentials)

    response_archive = client.patch("/api/messages/1")
    assert response_archive.status_code == 401

def test_archive_message_success(client: TestClient, session: Session):
    client.post("/api/contact", json=contact_credentials)
    token = get_token(client)

    # Step 1: Archive message (sets archived flag to True)
    response_archive = client.patch("/api/messages/1", headers={"Authorization": f"Bearer {token}"})
    assert response_archive.status_code == 200

    # Step 2: Verify if message is returned (archived messages won't be returned by GET endpoint)
    response = client.get("/api/messages", headers={"Authorization": f"Bearer {token}"})
    data = response.json()
    assert data == []

    # Step 3: Verify if message exists
    statement = select(ContactMessage)
    message = session.exec(statement).first()

def test_archive_archived_message(client: TestClient):
    client.post("/api/contact", json=contact_credentials)
    token = get_token(client)

    # Step 1: Archive message (sets archived flag to True)
    response_archive = client.patch("/api/messages/1", headers={"Authorization": f"Bearer {token}"})
    assert response_archive.status_code == 200

    # Step 2: Verify archivization of already archived message will not work (it tries to set the same flag value)
    response_archive = client.patch("/api/messages/1", headers={"Authorization": f"Bearer {token}"})
    assert response_archive.status_code == 409

def test_archive_nonexistent_message(client: TestClient):
    client.post("/api/contact", json=contact_credentials)
    token = get_token(client)

    response_archive = client.patch("/api/messages/2", headers={"Authorization": f"Bearer {token}"})
    assert response_archive.status_code == 404

def test_delete_message_no_token(client: TestClient):
    client.post("/api/contact", json=contact_credentials)
    
    response_delete = client.delete("/api/messages/1")
    assert response_delete.status_code == 401

def test_delete_message_success(client: TestClient):
    client.post("/api/contact", json=contact_credentials)
    token = get_token(client)

    # Step 1: Delete message
    response_delete = client.delete("/api/messages/1", headers={"Authorization": f"Bearer {token}"})
    assert response_delete.status_code == 200

    # Step 2: Verify if message exists
    response = client.get("/api/messages", headers={"Authorization": f"Bearer {token}"})
    data = response.json()
    assert data == []

def test_delete_nonexistent_message(client: TestClient):
    client.post("/api/contact", json=contact_credentials)
    token = get_token(client)
    
    response_delete = client.delete("/api/messages/2", headers={"Authorization": f"Bearer {token}"})
    assert response_delete.status_code == 404