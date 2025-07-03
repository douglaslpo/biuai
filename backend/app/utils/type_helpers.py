"""
Type helpers for better Pylance/mypy compatibility
"""

from typing import TYPE_CHECKING, cast
from fastapi import HTTPException
from starlette.exceptions import HTTPException as StarletteHTTPException

if TYPE_CHECKING:
    from typing import Union
    HttpExceptionType = Union[HTTPException, StarletteHTTPException]


def is_http_exception(error: Exception) -> bool:
    """Check if error is an HTTP exception type"""
    return isinstance(error, (HTTPException, StarletteHTTPException))


def get_http_status_code(error: Exception) -> int:
    """Get status code from HTTP exception"""
    if isinstance(error, HTTPException):
        return error.status_code
    elif isinstance(error, StarletteHTTPException):
        return error.status_code
    return 500


def get_http_detail(error: Exception) -> str:
    """Get detail message from HTTP exception"""
    if isinstance(error, HTTPException):
        return str(error.detail)
    elif isinstance(error, StarletteHTTPException):
        return str(error.detail)
    return str(error) 