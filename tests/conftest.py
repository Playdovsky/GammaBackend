import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.pool import StaticPool
from main import app
from database import get_session

@pytest.fixture(name="client")
def client_fixture():
    engine = create_engine(
        "sqlite://", 
        connect_args={"check_same_thread": False}, 
        poolclass=StaticPool
    )
    
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        def get_session_override():
            yield session

        app.dependency_overrides[get_session] = get_session_override

        with TestClient(app) as client:
            yield client

    app.dependency_overrides.clear()
    SQLModel.metadata.drop_all(engine)