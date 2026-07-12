from fastapi import APIRouter
from models import ContactMessage
from database import SessionDep

router = APIRouter(prefix="/api", tags=["Contact"])

@router.post("/contact")
async def contact(contactMsg: ContactMessage, session: SessionDep):
    session.add(contactMsg)
    session.commit()
    session.refresh(contactMsg)
    return contactMsg