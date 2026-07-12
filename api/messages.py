from fastapi import APIRouter
from sqlmodel import select
from database import SessionDep
from models import Message
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from api.auth import verify_jwt_token, bearer_scheme

router = APIRouter(prefix="/api", tags=["Messages"])

@router.get("/messages")
async def get_messages(session: SessionDep, credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    verify_jwt_token(credentials.credentials)
    messages = session.exec(select(Message).where(Message.archived == 0)).all()
    return messages

@router.patch("/messages/{message_id}")
async def archive_message(message_id: int, session: SessionDep, credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    verify_jwt_token(credentials.credentials)
    message = session.get(Message, message_id)
    
    if not message:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")
    
    message.archived = True
    session.commit()
    session.refresh(message)
    return {"message": "Message archived successfully"}

@router.delete("/messages/{message_id}")
async def delete_message(message_id: int, session: SessionDep, credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    verify_jwt_token(credentials.credentials)
    message = session.get(Message, message_id)
    
    if not message:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")
    
    session.delete(message)
    session.commit()
    return {"message": "Message deleted successfully"}