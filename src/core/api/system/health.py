from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

system_router = APIRouter(
    tags=['Система']
)

@system_router.get("/health")
async def health():
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"status": "ok"},
    )
