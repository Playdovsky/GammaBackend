from fastapi import APIRouter, HTTPException, status
from models import ContactMessage
from database import SessionDep
from sqlalchemy.exc import IntegrityError, DataError, OperationalError
import re
import string

router = APIRouter(prefix="/api", tags=["Contact"])

@router.post("/contact")
async def contact(contactMsg: ContactMessage, session: SessionDep):
    if (contactMsg.name is None or contactMsg.email is None or contactMsg.message is None):
        raise HTTPException(status_code = status.HTTP_422_UNPROCESSABLE_CONTENT, detail = "Missing fields")
    
    if (contactMsg.name.translate({ord(c): None for c in string.whitespace}) == "" or contactMsg.email.translate({ord(c): None for c in string.whitespace}) == "" or contactMsg.message.translate({ord(c): None for c in string.whitespace}) == ""):
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = "Empty fields")

    email_pattern = r"^[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$"
    if (re.match(email_pattern, contactMsg.email) is None):
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = "Invalid email address format")

    try:
        session.add(contactMsg)
        session.commit()
        session.refresh(contactMsg)
        return contactMsg
    except (IntegrityError, DataError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid contact form data: {str(e)}")
    except OperationalError:
        raise HTTPException(status_code = status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database unavailable")