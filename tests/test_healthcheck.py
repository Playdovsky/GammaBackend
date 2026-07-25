from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_healthcheck_success():
    response = client.get("/api/healthcheck")
    assert response.status_code == 200
    assert response.json() == {"message":"Service is running"}