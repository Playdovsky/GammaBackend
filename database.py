from sqlmodel import create_engine, select, SQLModel, Session
from typing_extensions import Annotated
from fastapi import Depends
from models import User
from pwdlib import PasswordHash
from config import settings
import logging

logger = logging.getLogger("uvicorn.info")

sqlite_file_name = "GammaDB.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    logger.info("Database initialized.")

def seed_admin_user():
    password_hash = PasswordHash.recommended()
    default_password = settings.SEED_USER_PASSWORD
    password_hashed = password_hash.hash(default_password)

    with Session(engine) as session:
        sample_user_exists = session.exec(select(User).where(User.username == "Mateusz")).first()

        if not sample_user_exists:
            logger.info("Sample user is not present in database. Creating...")
            session.add(User(username="Mateusz", password=password_hashed))
            session.commit()
            logger.info("Sample user has been added.")
        else:
            logger.info("Sample user already exists.")
    
def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]
