from datetime import datetime, timedelta, timezone
from typing_extensions import Annotated
from fastapi import Depends, FastAPI, HTTPException, status, Response, Cookie
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlmodel import Session, SQLModel, create_engine, select
from models import ContactMessage, LoginRequest, Token, User, LoginResponse
from fastapi.security import OAuth2PasswordBearer
import jwt
from jwt.exceptions import InvalidTokenError
from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS


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


### FastAPI App Setup ###


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


### Endpoints ###


@app.get("/api/healthcheck")
async def healthcheck():
    return {"message":"Service is running"}

@app.post("/api/contact")
async def contact(contactMsg: ContactMessage, session: SessionDep):
    session.add(contactMsg)
    session.commit()
    session.refresh(contactMsg)
    return contactMsg

@app.get("/api/messages")
async def get_messages(session: SessionDep):
    messages = session.exec(select(ContactMessage)).all()
    return messages

@app.delete("/api/messages/{message_id}")
async def delete_message(message_id: int, session: SessionDep):
    message = session.get(ContactMessage, message_id)
    if not message:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")
    session.delete(message)
    session.commit()
    return {"message": "Message deleted successfully"}

## Token lifecycle ##

def create_jwt_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_access_token(data: dict):
    return create_jwt_token(data, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))

def create_refresh_token(data: dict):
    return create_jwt_token(data, timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))

@app.post("/api/auth", response_model=LoginResponse)
async def auth(credentials: LoginRequest, response: Response, session: SessionDep):
    statement = select(User).where(User.username == credentials.username)
    user = session.exec(statement).first()

    if not user or user.password != credentials.password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": user.username})
    refresh_token = create_refresh_token(data={"sub": user.username})
    
    # TODO: Set secure=True in production (HTTPS)
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    )
    
    return {
        "accessToken": access_token,
        "user": {
            "username": user.username
        }
    }

@app.post("/api/refresh")
async def refresh(response: Response, refresh_token: str | None = Cookie(default=None), session: SessionDep = None):
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token missing"
        )
    
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    except InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
        
    statement = select(User).where(User.username == username)
    user = session.exec(statement).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        
    access_token = create_access_token(data={"sub": username})
    new_refresh_token = create_refresh_token(data={"sub": username})
    
    # TODO: Set secure=True in production (HTTPS)
    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    )
    
    return {"accessToken": access_token}

@app.post("/api/logout")
async def logout(response: Response):
    # TODO: Set secure=True in production (HTTPS)
    response.delete_cookie(
        key="refresh_token",
        httponly=True,
        samesite="lax",
        secure=False
    )
    return {"message": "Logged out successfully"}

async def get_current_user(session: SessionDep, token: str = Depends(OAuth2PasswordBearer(tokenUrl="/api/auth"))):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception

    statement = select(User).where(User.username == username)
    user = session.exec(statement).first()
    if user is None:
        raise credentials_exception
    
    return user
