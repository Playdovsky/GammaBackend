from fastapi import Depends, APIRouter, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlmodel import select
from database import SessionDep
from models import ContactMessage
from api.auth import verify_jwt_token, bearer_scheme
from sqlalchemy.exc import OperationalError

router = APIRouter(prefix="/api", tags=["Messages"])

@router.get("/messages")
async def get_messages(session: SessionDep, credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    verify_jwt_token(credentials.credentials)
    
    try:
        messages = session.exec(select(ContactMessage).where(ContactMessage.archived == 0)).all()
        return messages
    except OperationalError:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database unavailable")

@router.patch("/messages/{message_id}")
async def archive_message(message_id: int, session: SessionDep, credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    verify_jwt_token(credentials.credentials)
    message = session.get(ContactMessage, message_id)
    
    if not message:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")
    
    if (message.archived):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Message already archived")

    try:
        message.archived = True
        session.commit()
        session.refresh(message)
        return {"message": "Message archived successfully"}
    except OperationalError:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database unavailable")

@router.delete("/messages/{message_id}")
async def delete_message(message_id: int, session: SessionDep, credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    verify_jwt_token(credentials.credentials)
    message = session.get(ContactMessage, message_id)
    
    if not message:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")
    
    try:
        session.delete(message)
        session.commit()
        return {"message": "Message deleted successfully"}
    except OperationalError:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database unavailable")