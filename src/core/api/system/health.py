from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

system_router = APIRouter(
    tags=['Система']
)

@system_router.get(
    "/health",
    summary="Проверка доступности сервиса",
    description="""
    Возвращает признак работоспособности API.

    Права:
    - Не требуются.

    Сценарии:
    - Liveness/readiness проверка в оркестраторе.
    - Мониторинг доступности сервиса извне.
    """,
    response_description="Статус сервиса",
    responses={
        200: {
            "description": "Сервис доступен",
            "content": {"application/json": {"example": {"status": "ok"}}},
        }
    },
)
async def health():
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"status": "ok"},
    )
