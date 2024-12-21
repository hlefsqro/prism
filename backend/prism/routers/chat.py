from fastapi import APIRouter
from starlette.responses import StreamingResponse

from prism.operators.llm.chat_op import ChatReq, ChatOp
from prism.operators.llm.summariz_op import SummarizOp, SummaryResp, SummaryReq
from prism.routers import RestResponse

chat_router = APIRouter()


@chat_router.post("/api/prism/ai/summariz",
                  response_model=RestResponse[SummaryResp])
async def summariz(req: SummaryReq):
    """"""
    ret = await SummarizOp().predict(req)
    return RestResponse(data=ret)


@chat_router.get("/api/prism/ai/chat")
async def ai_search(req: ChatReq):
    return StreamingResponse(ChatOp.stream(req), media_type="text/event-stream")
