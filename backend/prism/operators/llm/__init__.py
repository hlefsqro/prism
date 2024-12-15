from abc import abstractmethod, ABC
from typing import Generic, TypeVar, Optional

from pydantic import BaseModel

BaseModelInput = TypeVar("BaseModelInput", bound=BaseModel, contravariant=True)
BaseModelOutput = TypeVar("BaseModelOutput", bound=BaseModel, contravariant=True)
LLmOutput = TypeVar("LLmOutput", covariant=True)


class LLMPredictOp(BaseModel, Generic[BaseModelInput, LLmOutput], ABC):
    llm_output_model: BaseModelOutput | str = str

    class Config:
        arbitrary_types_allowed = True

    @abstractmethod
    async def predict(self, input: BaseModelInput) -> Optional[LLmOutput]:
        pass

    async def _predict_default(self, input: BaseModelInput) -> Optional[LLmOutput]:
        processed_input = await self._pre_process(input)
        llm_output = await self._llm(processed_input)
        return await self._post_process(input, llm_output)

    async def _pre_process(self, input: BaseModelInput) -> BaseModelInput:
        return input

    async def _llm(self, input: BaseModelInput) -> Optional[LLmOutput]:
        return None

    async def _post_process(self, input: BaseModelInput, llm_output: Optional[LLmOutput]) -> Optional[LLmOutput]:
        return llm_output


class LLMStreamOp(object):

    @abstractmethod
    async def stream(self, input: BaseModelInput) -> Optional[LLmOutput]:
        pass
