from pydantic import BaseModel
from sqlmodel import Field, SQLModel
import datetime

class ContactMessage(SQLModel, table=True):
    __tablename__ = "ContactMessages"
    id: int | None = Field(default=None, primary_key=True)
    name: str
    email: str
    message: str
    published: datetime.datetime = Field(
            default_factory=lambda: datetime.datetime.now(datetime.UTC)
        )    
    archived: bool = Field(default=False)

class User(SQLModel, table=True):
    __tablename__ = "Users"
    id: int | None = Field(default=None, primary_key=True)
    username: str
    password: str

class LoginRequest(SQLModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    username: str

class LoginResponse(BaseModel):
    accessToken: str
    user: UserResponse
