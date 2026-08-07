import pytest
from fastapi.testclient import TestClient
from pwdlib import PasswordHash
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from database import get_session
from main import app
from models import User


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://", 
        connect_args={"check_same_thread": False}, 
        poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    
    with Session(engine) as session:
        yield session
    
    SQLModel.metadata.drop_all(engine)
    engine.dispose()

@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        yield session
    
    app.dependency_overrides[get_session] = get_session_override
    seed_test_admin_user(session)
    
    with TestClient(app, base_url="https://testserver") as client:
        yield client
    
    app.dependency_overrides.clear()

def seed_test_admin_user(session: Session):
    password_hash = PasswordHash.recommended()
    default_password = "a1#b2@c3!"
    password_hashed = password_hash.hash(default_password)
    session.add(User(username="Roman", password=password_hashed))
    session.commit()