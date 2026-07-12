from fastapi import APIRouter, HTTPException
from fastapi import Depends, APIRouter, HTTPException, status, Response, Cookie
from sqlmodel import select
from models import LoginRequest, User, LoginResponse
from jwt.exceptions import InvalidTokenError
from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordBearer, HTTPBearer
from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS
from database import SessionDep
import jwt

router = APIRouter(prefix="/api", tags=["Auth"])
bearer_scheme = HTTPBearer()

def verify_jwt_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")

        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        
        return username
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

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

def set_refresh_cookie(response: Response, token: str):
    response.set_cookie(
        key="refresh_token",
        value=token,
        httponly=True,
        samesite="lax",
        secure=False,   # TODO: Set secure=True in production (HTTPS)
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    )

def authenticate_user(credentials: LoginRequest, session: SessionDep) -> User:
    statement = select(User).where(User.username == credentials.username)
    user = session.exec(statement).first()

    if not user or user.password != credentials.password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    return user

@router.post("/token")
async def generate_token(credentials: LoginRequest, session: SessionDep):
    user = authenticate_user(credentials, session)
    
    return create_access_token(data={"sub": user.username})

@router.post("/auth", response_model=LoginResponse)
async def auth(credentials: LoginRequest, response: Response, session: SessionDep):
    user = authenticate_user(credentials, session)
    
    access_token = create_access_token(data={"sub": user.username})
    refresh_token = create_refresh_token(data={"sub": user.username})
    
    set_refresh_cookie(response, refresh_token)

    return {
        "accessToken": access_token,
        "user": {
            "username": user.username
        }
    }

@router.post("/refresh")
async def refresh(response: Response, refresh_token: str | None = Cookie(default=None), session: SessionDep = None):
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token missing"
        )
    
    username = verify_jwt_token(refresh_token)
        
    statement = select(User).where(User.username == username)
    user = session.exec(statement).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        
    access_token = create_access_token(data={"sub": username})
    new_refresh_token = create_refresh_token(data={"sub": username})
    
    set_refresh_cookie(response, new_refresh_token)

    return {"accessToken": access_token}

@router.post("/logout")
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