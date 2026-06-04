from typing_extensions import Annotated

from fastapi import Depends, FastAPI
from sqlmodel import Field, Session, SQLModel, create_engine, select

sqlite_file_name = "GammaDB.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

class ContactMessage(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    email: str
    message: str
    
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    
def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]

app = FastAPI()

@app.get("/healthcheck")
async def healthcheck():
    return {"message": "Service is running"}

@app.post("/contact")
async def contact(contactMsg: ContactMessage):
    return ContactMessage(name = contactMsg.name, email = contactMsg.email, message = contactMsg.message)

# TBD https://fastapi.tiangolo.com/tutorial/sql-databases/?h=database#create-the-tables:~:text=%3A%20True%7D-,Create%20a%20Session%20Dependency,%C2%B6,-A