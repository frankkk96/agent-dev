import json
import time
import redis

from openai import OpenAI
from typing import List, AsyncIterator
from openai.types.chat import ChatCompletionSystemMessageParam, ChatCompletionUserMessageParam

from agent_dev.agents.base import Post, ChatStatus
from agent_dev.stream.message import chat_message, Message
from agent_dev.contexts.context import parse_rss_to_context
from agent_dev.stream.chunks import StatusChunk, ContentChunk, ErrorChunk


class RSSAgent:
    def __init__(self, name: str, base_url: str, api_key: str, model: str, feeds: dict, timeout: int, post_prompt: str, redis_host: str, redis_port: int, redis_password: str):
        self.name = name
        self.base_url = base_url
        self.api_key = api_key
        self.model = model
        self.feeds = feeds
        self.timeout = timeout
        self.post_prompt = post_prompt
        self.redis = redis.Redis(
            host=redis_host,
            port=redis_port,
            password=redis_password,
            ssl=True
        )

    async def stream(self, req_messages: List[Message]) -> AsyncIterator[str]:
        try:
            yield StatusChunk(status=ChatStatus.STREAMING.value).to_sse()
            client = OpenAI(
                base_url=self.base_url, api_key=self.api_key)
            messages = [chat_message(
                message) for message in req_messages]
            context = parse_rss_to_context(self.feeds)
            messages.insert(0, ChatCompletionSystemMessageParam(
                role="system",
                content=context
            ))
            stream = client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=True,
            )
            for _chunk in stream:
                content = _chunk.choices[0].delta.content if hasattr(
                    _chunk.choices[0].delta, 'content') else None
                if content:
                    yield ContentChunk(text=content).to_sse()

        except Exception as e:
            yield ErrorChunk(text="Service Error: " + str(e)).to_sse()
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
            base_url=self.base_url, api_key=self.api_key)
        response = client.chat.completions.create(
            model=self.model,
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
