import logging
from enum import IntEnum
from typing import TypeVar, Generic, Optional

import fastapi
from fastapi.responses import ORJSONResponse
from openai import BaseModel
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from prism.common.otel import Otel

T = TypeVar('T')

logger = logging.getLogger(__name__)


class RestResponse(BaseModel, Generic[T]):
    code: int = 0
    msg: str = "ok"
    data: Optional[T] = None


class ErrorCode(IntEnum):
    INTERNAL_ERROR = 10000
    AUTH_ERROR = 10001
    RATELIMITER = 10002


async def exception_handler(request: fastapi.Request, exc):
    """"""
    logger.error("Global Exception handler", exc_info=True)
    ret = RestResponse(code=ErrorCode.INTERNAL_ERROR, msg='The server is busy')
    return ORJSONResponse(
        ret.model_dump(),
        status_code=200
    )


healthz_list = ["/healthz/readiness", "/healthz/liveness"]


class LogMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        tid = Otel.get_cur_tid()
        if tid and len(tid) > 1:
            response.headers['tid'] = tid

        return response
