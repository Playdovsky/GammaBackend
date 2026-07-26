from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from api import auth, contact, healthcheck, messages
from database import create_db_and_tables, seed_admin_user, seed_sample_messages

### FastAPI App Setup ###

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    seed_admin_user()
    seed_sample_messages()
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