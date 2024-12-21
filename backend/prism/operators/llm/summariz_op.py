from typing import List

from pydantic import BaseModel, Field

from prism.operators.llm import LLMPredictOp

DEFAULT_HUMAN_PROMPT = """\
You are a helpful assistant. Please summarize the webpage content provided by the user.

## Requirements:
- The summarized content must be as detailed and objective as possible
- The output should be in English
- Provide in-depth explanations for key areas, key technologies, and key logical relationships
- If there is any data information, perform data analysis
- 
- The summary should be as detailed as possible, with more than 300 words.

The webpage content is as follows:

{content}\
"""


class Summarize(BaseModel):
    """
    Summarize
    """
    summary: str = Field(..., title="Summary")
    key_points: List[str] = Field(..., title="KeyPoints")


class Post(BaseModel):
    """
    Post
    """
    username: str = Field(..., title="Username")
    summarize: Summarize = Field(..., title="Summarize")
    posttime: str = Field(..., title="Posttime. YYYY-MM-DDTHH:MM:SSZ")


class SummaryResp(BaseModel):
    """
    SummaryResp
    """
    summaries: List[Post] = Field(default_factory=list, description="Summaries List")


class SummaryReq(BaseModel):
    content: str


class SummarizOp(LLMPredictOp):
    llm_output_model: type[BaseModel] | str = SummaryResp
    default_human_prompt: str = DEFAULT_HUMAN_PROMPT

    async def predict(self, req: SummaryReq) -> SummaryResp:
        return await self._predict_default(req)

    async def stream(self, input: SummaryReq) -> SummaryResp:
        raise NotImplementedError
