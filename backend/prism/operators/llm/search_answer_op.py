from typing import List, Any, AsyncIterator, Optional

from langchain_core.documents import Document
from pydantic import BaseModel, computed_field

from prism.operators.llm import LLMPredictOp

DEFAULT_HUMAN_PROMPT = """\
你是非常出色的 AI 搜索助理。你的任务是根据上下文回答用户提出的问题。

## 要求
- 充分利用上下文信息，但也不要盲目地逐字重复上下文
- 答案目标语言: 中文
- 答案必须 简洁、正确、准确

## 以下是一组上下文：

{context}

## 以下是用户问题

{user_input}\
"""


class SearchAnswerReq(BaseModel):
    user_input: str
    resources: Optional[List[Document]] = None

    @computed_field
    @property
    def context(self) -> str:
        if not self.resources:
            return "未检索到相关上下文，请用你的知识回答用户问题"

        context = ""
        for doc in self.resources:
            if doc.page_content:
                context += f"{doc.page_content}"
                if doc.metadata.get('created_at'):
                    context += f"created_at \n{doc.metadata.get('created_at')}"
                context += "\n\n"
        return context


class SearchAnswerOp(LLMPredictOp):
    default_human_prompt: str = DEFAULT_HUMAN_PROMPT

    async def predict(self, input: SearchAnswerReq) -> Any:
        raise NotImplementedError()

    async def stream(self, input: SearchAnswerReq) -> AsyncIterator:
        async for chunk in self._stream_default(input):
            yield chunk
