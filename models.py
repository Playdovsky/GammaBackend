from pydantic import BaseModel
from sqlmodel import Field, SQLModel

class ContactMessage(SQLModel, table=True):
    __tablename__ = "ContactMessages"
    id: int | None = Field(default=None, primary_key=True)
    name: str
    email: str
    message: str
    archived: bool

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
