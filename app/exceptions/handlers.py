from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.exceptions.config import ExceptionConfig
from app.exceptions.exceptions import InvalidColumnsError, UserIntegrityError
from app.schema.exceptions import ErrorResponse

config = ExceptionConfig()


async def invalid_columns_error_exception_handler(
    request: Request,
    exc: InvalidColumnsError,
) -> JSONResponse:
    conf = config.invalid_columns_error
    return JSONResponse(
        status_code=conf.status_code,
        content=dict(ErrorResponse(message=conf.message)),
    )


async def request_validation_error_exception_handler(
    request: Request,
    exc: InvalidColumnsError,
) -> JSONResponse:
    conf = config.request_validation_error
    return JSONResponse(
        status_code=conf.status_code,
        content=dict(ErrorResponse(message=conf.message)),
    )


async def user_integrity_exception_handler(
    request: Request, exc: InvalidColumnsError
) -> JSONResponse:
    conf = config.user_integrity_exception
    return JSONResponse(
        status_code=conf.status_code,
        content=dict(ErrorResponse(message=conf.message)),
    )


def exception_handler(app: FastAPI) -> None:
    app.add_exception_handler(
        InvalidColumnsError,
        invalid_columns_error_exception_handler,
    )
    app.add_exception_handler(
        RequestValidationError,
        request_validation_error_exception_handler,
    )
    app.add_exception_handler(UserIntegrityError, user_integrity_exception_handler)
