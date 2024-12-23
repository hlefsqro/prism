from typing import List, Any, AsyncIterator, Optional

from langchain_core.documents import Document
from pydantic import BaseModel, computed_field

from prism.operators.llm import LLMPredictOp

DEFAULT_HUMAN_PROMPT = """\
You are a helpful AI analyze assistant. Your task is to analyze the user's question based on the context.

## Requirements
- You should repeatedly understand the context and think and analyze why this context causes the user's question, but don't blindly repeat the context verbatim
- You should first summarize the conclusions of your analysis
- You should analyze key points from multiple angles
- You need to leverage data in context
- You are an expert in analysis. The output is what you think after learning the context. Don't emphasize that it comes from the context.
- The output should be markdown
- The output should be in English

<Output format>

## **Summary**

... ...

## **Key Points**

- **Point A**: key point A details
- **Point B**: key point B details
... ...

</Output format>

## Below is a set of context

{context}

## Below is the user’s question

{user_input}\
"""

DEFAULT_HUMAN_PROMPT_1 = """\
You are a helpful AI search assistant. Your task is to answer the questions asked by users based on the context.

## Requirements
- Make full use of context information, but don't blindly repeat the context verbatim
- The answer must be concise, correct and accurate
- The output should be in English.

## Below is a set of context

{context}

## Below is the user’s question

{user_input}\
"""


class SearchAnswerReq(BaseModel):
    user_input: str
    resources: Optional[List[Document]] = None

    @computed_field
    @property
    def context(self) -> str:
        if not self.resources:
            return "No relevant context was found. Please use your knowledge to answer the user's question."

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
