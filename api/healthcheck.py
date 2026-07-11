from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["Health"])

@router.get("/healthcheck")
async def healthcheck():
    return {"message":"Service is running"}