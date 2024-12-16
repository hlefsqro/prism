from typing import Optional

from langchain.chains.base import Chain
from langchain_core.output_parsers import StrOutputParser
from pydantic import BaseModel

from prism.chains.model_manager import get_chat_llm_model
from prism.chains.prompt_manager import get_chat_prompt


def create_simple_chain(default_human_prompt: str,
                        llm_output_model: Optional[type[BaseModel] | str] = None) -> Chain:
    chat_prompt = get_chat_prompt(default_human_prompt=default_human_prompt)
    chat_llm = get_chat_llm_model()

    if isinstance(llm_output_model, type) and issubclass(llm_output_model, BaseModel):
        return chat_prompt | chat_llm.with_structured_output(llm_output_model)
    else:
        return chat_prompt | chat_llm | StrOutputParser()
