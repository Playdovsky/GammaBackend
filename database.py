import logging
from typing import Annotated

from fastapi import Depends
from pwdlib import PasswordHash
from sqlmodel import Session, SQLModel, create_engine, or_, select

from config import settings
from models import ContactMessage, User

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
        sample_user_exists = session.exec(select(User).where(User.username == settings.SEED_USER_USERNAME)).first()

        if not sample_user_exists:
            logger.info("Sample user is not present in database. Creating...")
            session.add(User(username=settings.SEED_USER_USERNAME, password=password_hashed))
            session.commit()
            logger.info("Sample user has been added.")
        else:
            logger.info("Sample user already exists.")

sample_messages = [
    ContactMessage(name = "David", email = "ambro1996@protonmail.com", message = "Hello World!"),
    ContactMessage(name = "Matthew", email = "matthew_stick@gmail.com", message = "This is a test message!"),
    ContactMessage(name = "Carlos", email = "carlos.fontanciones@wp.pl", message = "PDW PDW for all good folks out there!")
]

def seed_sample_messages():
    with Session(engine) as session:
        existing_messages = set(
            session.exec(
                select(ContactMessage.email).where(
                    or_(
                        ContactMessage.email == "ambro1996@protonmail.com", 
                        ContactMessage.email == "matthew_stick@gmail.com", 
                        ContactMessage.email == "carlos.fontanciones@wp.pl"
                    )
                )
            ).all()
        )

        if len(existing_messages) < 3:
            for sample in sample_messages:
                if sample.email not in existing_messages:
                    session.add(sample)

            session.commit()
            logger.info("Missing sample messages have been added")
        else:
            logger.info("All sample messages already exist")


def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]
