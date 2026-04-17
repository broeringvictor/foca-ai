from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, Response
from pydantic import ValidationError
from typing import cast

from app.api.errors.exceptions import (
    AppValueError,
)
from app.api.errors.formatters import format_errors


async def validation_error_handler(request: Request, exc: Exception) -> Response:
    err = cast(ValidationError, exc)
    return JSONResponse(
        status_code=422,
        content={"detail": format_errors(err.errors())},
    )


async def request_validation_error_handler(
    request: Request, exc: Exception
) -> Response:
    err = cast(RequestValidationError, exc)
    return JSONResponse(
        status_code=422,
        content=dict(detail=format_errors(err.errors())),
    )


async def value_error_handler(request: Request, exc: Exception) -> Response:
    err = cast(ValueError, exc)
    return JSONResponse(
        status_code=422,
        content={"detail": [{"field": "geral", "message": str(err), "source": None}]},
    )


def _app_value_error_response(err: Exception, status_code: int) -> Response:
    cast_err = cast(AppValueError, err)
    return JSONResponse(
        status_code=status_code,
        content={
            "detail": [
                {
                    "field": cast_err.field,
                    "message": str(cast_err),
                    "source": cast_err.source,
                }
            ]
        },
    )


async def bad_request_error_handler(request: Request, exc: Exception) -> Response:
    return _app_value_error_response(exc, status_code=400)


async def conflict_error_handler(request: Request, exc: Exception) -> Response:
    return _app_value_error_response(exc, status_code=409)


async def not_found_error_handler(request: Request, exc: Exception) -> Response:
    return _app_value_error_response(exc, status_code=404)
