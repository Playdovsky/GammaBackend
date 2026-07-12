from fastapi import APIRouter, HTTPException, status
from models import ContactMessage
from database import SessionDep
from sqlalchemy.exc import IntegrityError, DataError, OperationalError
import re

router = APIRouter(prefix="/api", tags=["Contact"])

@router.post("/contact")
async def contact(contactMsg: ContactMessage, session: SessionDep):
    email_pattern = r"^[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$" 
    if (re.match(email_pattern, contactMsg.email) is None):
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = f"Invalid email address format")

    try:
        session.add(contactMsg)
        session.commit()
        session.refresh(contactMsg)
        return contactMsg
    except (IntegrityError, DataError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid contact form data: {str(e)}")
    except OperationalError:
        raise HTTPException(status_code = status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database unavailable")