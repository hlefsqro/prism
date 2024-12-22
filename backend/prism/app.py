import logging
from contextlib import asynccontextmanager

import fastapi
import uvicorn
from starlette.middleware.cors import CORSMiddleware

from prism.common.config import SETTINGS
from prism.common.log import Log
from prism.common.otel import Otel, OtelFastAPI
from prism.routers import exception_handler, LogMiddleware
from prism.routers.ai_search import ai_search_router
from prism.routers.chat import chat_router
from prism.routers.route_probe import probe_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: fastapi.FastAPI):
    logger.info(f"prism starting on {SETTINGS.HOST}:{SETTINGS.PORT}")
    yield
    logger.info("prism shutting down")


app = fastapi.FastAPI(docs_url=None, redoc_url=None, title=SETTINGS.APP_NAME, lifespan=lifespan)
[app.include_router(router) for router in [probe_router, ai_search_router, chat_router]]


@app.exception_handler(Exception)
async def default_exception_handler(request: fastapi.Request, exc):
    return await exception_handler(request, exc)


if __name__ == "__main__":
    Log.init()
    Otel.init()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(LogMiddleware)
    OtelFastAPI.init(app)

    uvicorn.run(app, host=SETTINGS.HOST, port=SETTINGS.PORT, log_level="warning")
