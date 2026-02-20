from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from src.core.exceptions.base import BaseServiceError


def api_response(result):
    if isinstance(result, BaseServiceError):
        return JSONResponse(
            status_code=result.status_code,
            content={
                "success": False,
                "error": {
                    "code": result.code,
                    "message": result.message,
                    "details": result.details,
                },
            },
        )

    return JSONResponse(
        status_code=200,
        content=jsonable_encoder(
            {
                "success": True,
                "data": result,
            }
        ),
    )

