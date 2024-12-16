from abc import ABC, abstractmethod
from typing import TypeVar, Optional, List

from langchain_core.documents import Document
from pydantic import BaseModel

BaseModelInput = TypeVar("BaseModelInput", bound=BaseModel, contravariant=True)


class SearchOp(ABC):

    @abstractmethod
    async def search(self, input: BaseModelInput) -> Optional[List[Document]]:
        raise NotImplementedError
