from typing_extensions import Annotated
from fastapi import Depends, FastAPI
from contextlib import asynccontextmanager
from sqlmodel import Session, SQLModel, create_engine
from models import ContactMessage

### Database & Session setup ###

sqlite_file_name = "GammaDB.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    
def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

### Endpoints ###

app = FastAPI()

@asynccontextmanager
async def lifespan():
    create_db_and_tables()

@app.get("/healthcheck")
async def healthcheck():
    return {"message": "Service is running"}

@app.post("/contact")
async def contact(contactMsg: ContactMessage, session: SessionDep):
    session.add(contactMsg)
    session.commit()
    session.refresh(contactMsg)
    return contactMsg