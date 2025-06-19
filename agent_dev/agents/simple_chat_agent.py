import uuid
from openai import OpenAI
from typing import List, AsyncIterator

from agents.base import ChatStatus, ModelProvider
from stream.message import Message, chat_message
from stream.chunks import StatusChunk, ContentChunk, ReasoningChunk, ErrorChunk


class SimpleChatAgent:
    async def stream(self, model: ModelProvider, messages: List[Message]) -> AsyncIterator[str]:
        try:
            message_id = str(uuid.uuid4())

            yield StatusChunk(status=ChatStatus.STREAMING.value, message_id='status-' + message_id).to_sse()
            client = OpenAI(base_url=model.base_url, api_key=model.api_key)
            chat_messages = [chat_message(
                message) for message in messages]

            stream = client.chat.completions.create(
                model=model.model,
                messages=chat_messages,
                stream=True,
            )
            for _chunk in stream:
                content = _chunk.choices[0].delta.content if hasattr(
                    _chunk.choices[0].delta, 'content') else None
                reasoning = None
                if hasattr(_chunk.choices[0].delta, 'reasoning_content'):
                    reasoning = _chunk.choices[0].delta.reasoning_content
                elif hasattr(_chunk.choices[0].delta, 'reasoning'):
                    reasoning = _chunk.choices[0].delta.reasoning

                if content:
                    yield ContentChunk(text=content, message_id='content-' + message_id).to_sse()
                elif reasoning:
                    yield ReasoningChunk(text=reasoning, message_id='reasoning-' + message_id).to_sse()
                else:
                    message_id = str(uuid.uuid4())

        except Exception as e:
            yield ErrorChunk(text="Service Error: " + str(e), message_id='error-' + message_id).to_sse()
        finally:
            yield "data: [DONE]\n\n"
