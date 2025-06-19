from typing import Optional
from pydantic import BaseModel
from openai.types.chat import ChatCompletionMessageParam


class Message(BaseModel):
    role: str
    text: str
    image_url: Optional[str] = None


def chat_message(message: Message) -> ChatCompletionMessageParam:
    if message.image_url != None and message.image_url != "":
        return {
            "role": message.role,
            "content": [
                {
                    "type": "image_url",
                    "image_url": {"url": message.image_url},
                },
                {
                    "type": "text",
                    "text": message.text,
                },
            ],
        }
    else:
        return {
            "role": message.role,
            "content": message.text,
        }


def tc_messages(tc_id: str, tc_name: str, tc_args: str, tc_result: str) -> ChatCompletionMessageParam:
    return [
        {
            "role": "assistant",
            "tool_calls": [{"id": tc_id, "function": {"name": tc_name, "arguments": tc_args}}],
        },
        {
            "role": "tool",
            "content": tc_result,
            "tool_call_id": tc_id,
        },
    ]
