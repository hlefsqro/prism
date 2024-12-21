from fastapi import APIRouter

from prism.operators.llm.summariz_op import SummarizOp, SummaryResp, SummaryReq
from prism.routers import RestResponse

chat_router = APIRouter()


@chat_router.post("/api/prism/ai/summariz",
                  response_model=RestResponse[SummaryResp])
async def summariz(req: SummaryReq):
    """"""
    ret = await SummarizOp().predict(SummaryReq(user_input=req.content))
    return RestResponse(data=ret)
