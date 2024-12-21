from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate


def get_chat_prompt(default_human_prompt,
                    default_system_prompt=None,
                    image_url=None) -> ChatPromptTemplate:
    system = default_system_prompt
    human = default_human_prompt

    human_message = HumanMessagePromptTemplate.from_template(human)

    if system is None:
        return ChatPromptTemplate.from_messages([human_message])

    system_message = SystemMessage(content=system)

    if image_url is None:
        return ChatPromptTemplate.from_messages([system_message, human_message])

    img_messag = HumanMessage(
        content=[
            {
                "type": "image_url",
                "image_url": {"url": image_url},
            },
        ]
    )
    return ChatPromptTemplate.from_messages([system_message, human_message, img_messag])
