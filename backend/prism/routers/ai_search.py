from fastapi import APIRouter, Query
from sse_starlette import EventSourceResponse

from prism.agent.ai_search_agent import AISearchAgent

ai_search_router = APIRouter()


@ai_search_router.get("/api/prism/ai/search")
async def ai_search(query: str = Query(...)):
    return EventSourceResponse(AISearchAgent().search(query))
