from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from typing import Any, Dict, List

class AppException(Exception):
    """Exception de base pour l'application"""
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(self.detail)

async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Gestionnaire pour les exceptions de l'application"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Gestionnaire pour les exceptions HTTP standard"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Gestionnaire pour les erreurs de validation des requêtes"""
    errors: List[Dict[str, Any]] = []
    for error in exc.errors():
        error_detail = {
            "loc": error["loc"],
            "msg": error["msg"],
            "type": error["type"],
        }
        errors.append(error_detail)
    
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Validation error",
            "errors": errors
        },
    )