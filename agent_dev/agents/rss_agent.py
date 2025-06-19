import json
import time
import uuid

from openai import OpenAI
from typing import List, AsyncIterator
from openai.types.chat import ChatCompletionSystemMessageParam, ChatCompletionUserMessageParam

from utils.redis import Redis
from stream.message import chat_message, Message
from contexts.context import parse_rss_to_context
from agents.base import Post, ChatStatus, ModelProvider
from stream.chunks import StatusChunk, ContentChunk, ErrorChunk


class RSSAgent:
    def __init__(self, name: str, model: ModelProvider, redis: Redis, feeds: dict, post_prompt: str):
        self.name = name
        self.model = model
        self.feeds = feeds
        self.timeout = 3600
        self.post_prompt = post_prompt
        self.redis = redis

    async def stream(self, messages: List[Message]) -> AsyncIterator[str]:
        try:
            message_id = str(uuid.uuid4())

            yield StatusChunk(status=ChatStatus.STREAMING.value, message_id="status:" + message_id).to_sse()
            client = OpenAI(base_url=self.model.base_url,
                            api_key=self.model.api_key)
            chat_messages = [chat_message(message) for message in messages]
            context = parse_rss_to_context(self.feeds)
            chat_messages.insert(0, ChatCompletionSystemMessageParam(
                role="system",
                content=context
            ))

            stream = client.chat.completions.create(
                model=self.model.model,
                messages=chat_messages,
                stream=True,
            )
            for _chunk in stream:
                content = _chunk.choices[0].delta.content if hasattr(
                    _chunk.choices[0].delta, 'content') else None
                if content:
                    yield ContentChunk(text=content, message_id="content:" + message_id).to_sse()

        except Exception as e:
            yield ErrorChunk(text="Service Error: " + str(e), message_id="error:" + message_id).to_sse()
        finally:
            yield "data: [DONE]\n\n"

    async def get_post(self) -> Post:
        post = self.redis.get(f"{self.name}:post")
        if post:
            return Post(**json.loads(post))
        else:
            return None

    async def update_post(self) -> Post:
        prompt = self.post_prompt
        context = parse_rss_to_context(self.feeds)
        client = OpenAI(
            base_url=self.model.base_url, api_key=self.model.api_key)
        response = client.chat.completions.create(
            model=self.model.model,
            messages=[
                ChatCompletionSystemMessageParam(
                    role="system",
                    content=context
                ),
                ChatCompletionUserMessageParam(
                    role="user",
                    content=prompt
                )
            ],
            timeout=self.timeout
        )
        post = Post(id=response.id, timestamp=int(time.time() * 1000),
                    content=response.choices[0].message.content)
        self.redis.set(f"{self.name}:post", json.dumps(post.model_dump()))
