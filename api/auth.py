from fastapi import Cookie, APIRouter, HTTPException, status, Response
from fastapi.security import HTTPBearer
from sqlmodel import select
from models import LoginRequest, User, LoginResponse
from jwt.exceptions import InvalidTokenError
from datetime import datetime, timedelta, timezone
from config import settings
from database import SessionDep
from sqlalchemy.exc import OperationalError
from pwdlib import PasswordHash
import jwt

router = APIRouter(prefix="/api", tags=["Auth"])
bearer_scheme = HTTPBearer()

def verify_jwt_token(token: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")

        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        
        return username
    except InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

def create_jwt_token(data: dict, expires_delta: timedelta):
    try:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + expires_delta
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
    except TypeError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=f"Invalid data type: {str(e)}")

def create_access_token(data: dict):
    return create_jwt_token(data, timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))

def create_refresh_token(data: dict):
    return create_jwt_token(data, timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS))

def set_refresh_cookie(response: Response, token: str):
    response.set_cookie(
        key="refresh_token",
        value=token,
        httponly=True,
        samesite=settings.COOKIE_SAMESITE,
        secure=settings.COOKIE_SECURE,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    )

def authenticate_user(credentials: LoginRequest, session: SessionDep) -> User:
    statement = select(User).where(User.username == credentials.username)
    user = session.exec(statement).first()

    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    password_hash = PasswordHash.recommended()
    validation_result = password_hash.verify(credentials.password, user.password)

    if not validation_result:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    return user

@router.post("/token")
async def generate_token(credentials: LoginRequest, session: SessionDep):
    try:
        user = authenticate_user(credentials, session)
        return create_access_token(data={"sub": user.username})
    except OperationalError:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database unavailable")


@router.post("/auth", response_model=LoginResponse)
async def auth(credentials: LoginRequest, response: Response, session: SessionDep):
    try:
        user = authenticate_user(credentials, session)
    except OperationalError:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database unavailable")

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
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token missing")
    
    username = verify_jwt_token(refresh_token)

    try:   
        statement = select(User).where(User.username == username)
        user = session.exec(statement).first()
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    except OperationalError:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database unavailable")

    access_token = create_access_token(data={"sub": username})
    new_refresh_token = create_refresh_token(data={"sub": username})
    
    set_refresh_cookie(response, new_refresh_token)
    
    return {"accessToken": access_token}

@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(
        key="refresh_token",
        httponly=True,
        samesite=settings.COOKIE_SAMESITE,
        secure=settings.COOKIE_SECURE
    )
    return {"message": "Logged out successfully"}

# not used anywhere, but could be useful in the future if we want to get the current user from the token
#async def get_current_user(session: SessionDep, token: str = Depends(OAuth2PasswordBearer(tokenUrl="/api/auth"))):
#    credentials_exception = HTTPException(
#        status_code=status.HTTP_401_UNAUTHORIZED,
#        detail="Could not validate credentials",
#        headers={"WWW-Authenticate": "Bearer"},
#    )
#
#    try:
#        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
#        username: str = payload.get("sub")
#        if username is None:
#            raise credentials_exception
#    except InvalidTokenError:
#        raise credentials_exception
#
#    statement = select(User).where(User.username == username)
#    user = session.exec(statement).first()
#    if user is None:
#        raise credentials_exception
#    
#    return user