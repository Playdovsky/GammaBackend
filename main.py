from datetime import datetime, timedelta, timezone
from typing_extensions import Annotated
from fastapi import Depends, FastAPI, APIRouter, HTTPException, status, Response, Cookie
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlmodel import Session, SQLModel, create_engine, select
from models import ContactMessage, LoginRequest, Token, User, LoginResponse
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials
from api import auth, contact, healthcheck, messages
import jwt
from jwt.exceptions import InvalidTokenError
from database import create_db_and_tables, get_session, SessionDep
from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS


### Database & Session setup ###


### FastAPI App Setup ###


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)
router = APIRouter()

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


app.include_router(auth.router)
app.include_router(contact.router)
app.include_router(messages.router)
app.include_router(healthcheck.router)