import requests

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


def image_gen_message(message: Message) -> ChatCompletionMessageParam:
    if message.image_url != None:
        file_path = "/tmp/" + message.image_url.split("/")[-1]
        response = requests.get(message.image_url)
        if response.status_code != 200:
            raise Exception(f"Failed to get image from {message.image_url}")
        with open(file_path, "wb") as f:
            f.write(response.content)
        return {
            "prompt": message.text,
            "image": open(file_path, "rb"),
        }
    else:
        return {
            "prompt": message.text,
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
