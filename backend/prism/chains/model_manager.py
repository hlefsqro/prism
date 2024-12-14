from typing import Any

from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI


def get_chat_llm_model(key: Any = None) -> BaseChatModel:
    # TODO
    model_name = "gpt-4o-2024-08-06"
    temperature = 0.01
    return ChatOpenAI(model_name=model_name, temperature=temperature)
