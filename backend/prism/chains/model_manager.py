from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI

from prism.chains.log_callback import LLMLogCallbackHandler


def get_chat_llm_model() -> BaseChatModel:
    # TODO
    model_name = "gpt-4o-2024-08-06"
    temperature = 0.01
    return ChatOpenAI(model_name=model_name, temperature=temperature, callbacks=[LLMLogCallbackHandler()])
