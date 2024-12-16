from typing import List, AsyncIterator, Optional

from langchain_core.documents import Document
from pydantic import BaseModel, computed_field, Field

from prism.operators.llm import LLMPredictOp, BaseModelInput
from prism.operators.llm.search_answer_op import SearchAnswerReq

DEFAULT_HUMAN_PROMPT = """\
你是非常出色的 AI 搜索助理。你的任务是根据用户原始问题和上下文提出相关问题。

## 要求
- 充分利用上下文信息
- 生成 3 个相关问题
- 每个相关问题不超过 20 个字

## 以下是一组上下文：

{context}

## 以下是用户原始问题

{user_input}\
"""


class Questions(BaseModel):
    """
    Questions
    """
    questions: List[str] = Field(default_factory=list, description="相关问题列表")


class RelatedQuestionsReq(BaseModel):
    user_input: str
    resources: Optional[List[Document]] = None

    @computed_field
    @property
    def context(self) -> str:
        if not self.resources:
            return "无相关上下文，请自行发挥"

        context = ""
        for doc in self.resources:
            if doc.page_content:
                context += f"{doc.page_content}"
                if doc.metadata.get('created_at'):
                    context += f"created_at \n{doc.metadata.get('created_at')}"
                context += "\n\n"
        return context


class RelatedQuestionsOp(LLMPredictOp):
    llm_output_model: type[BaseModel] | str = Questions
    default_human_prompt: str = DEFAULT_HUMAN_PROMPT

    async def predict(self, req: SearchAnswerReq) -> Questions:
        return await self._predict_default(req)

    async def stream(self, input: BaseModelInput) -> AsyncIterator:
        raise NotImplementedError
