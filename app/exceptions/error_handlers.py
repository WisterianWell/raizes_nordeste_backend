import logging
from datetime import datetime, timezone
from http import HTTPStatus

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)

ERROR_CODES = {
    status.HTTP_400_BAD_REQUEST: "BAD_REQUEST",
    status.HTTP_401_UNAUTHORIZED: "UNAUTHORIZED",
    status.HTTP_403_FORBIDDEN: "FORBIDDEN",
    status.HTTP_404_NOT_FOUND: "NOT_FOUND",
    status.HTTP_409_CONFLICT: "CONFLICT",
    status.HTTP_422_UNPROCESSABLE_ENTITY: "VALIDATION_ERROR",
    status.HTTP_500_INTERNAL_SERVER_ERROR: "INTERNAL_SERVER_ERROR",
}

def _error_code(status_code: int) -> str:
    if status_code in ERROR_CODES:
        return ERROR_CODES[status_code]
    try:
        return HTTPStatus(status_code).phrase.upper().replace(" ", "_")
    except ValueError:
        return "ERROR"

def _build_envelope(
    request: Request,
    status_code: int,
    message: str,
    error_code: str | None = None,
    details: list[dict] | None = None,
) -> dict:
    return {
        "error": error_code or _error_code(status_code),
        "message": message,
        "details": details or [],
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "path": request.url.path,
    }

def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        message = exc.detail if isinstance(exc.detail, str) else "Erro na requisição."
        error_code = getattr(exc, "error_code", None)
        details = getattr(exc, "details", None)
        envelope = _build_envelope(request, exc.status_code, message, error_code=error_code, details=details)
        return JSONResponse(status_code=exc.status_code, content=envelope, headers=exc.headers)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        details = [{
                "field": ".".join(str(p) for p in err["loc"] if p != "body"),
                "issue": err["msg"]}
            for err in exc.errors()
        ]
        envelope = _build_envelope(
            request,
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            "Erro de validação nos dados enviados.",
            error_code="VALIDATION_ERROR",
            details=details,
        )
        return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content=envelope)

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Erro não tratado em %s", request.url.path)
        envelope = _build_envelope(
            request, status.HTTP_500_INTERNAL_SERVER_ERROR, "Erro interno no servidor."
        )
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=envelope)
