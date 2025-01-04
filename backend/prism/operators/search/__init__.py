from abc import ABC, abstractmethod
from typing import TypeVar, Optional, List

from langchain_core.documents import Document
from pydantic import BaseModel

from prism.common.config import SETTINGS

BaseModelInput = TypeVar("BaseModelInput", bound=BaseModel, contravariant=True)


class SearchOp(ABC):

    @abstractmethod
    async def search(self, input: BaseModelInput) -> Optional[List[Document]]:
        raise NotImplementedError


def print_token_with_masking(token: str):
    if len(token) > 8:
        masked_token = token[:4] + '*' * (len(token) - 8) + token[-4:]
        print(masked_token)


def token_generator(tokens):
    while True:
        for token in tokens:
            yield token


token_gen = token_generator(SETTINGS.X_BEARER_TOKENS)


def get_x_token() -> str:
    cur_token = next(token_gen)
    print_token_with_masking(cur_token)
    return cur_token
