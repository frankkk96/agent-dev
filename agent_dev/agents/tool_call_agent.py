import uuid
from openai import OpenAI
from typing import List, AsyncIterator

from tools import Tool
from agents.base import ChatStatus, ModelProvider
from stream.message import Message, chat_message, tc_messages
from stream.chunks import StatusChunk, ContentChunk, ContextChunk, ErrorChunk


class ToolCallAgent:
    def __init__(self, model: ModelProvider, tools: List[Tool]):
        self.model = model
        self.tools = tools

    async def stream(self, messages: List[Message]) -> AsyncIterator[str]:
        try:
            message_id = str(uuid.uuid4())

            yield StatusChunk(status=ChatStatus.STREAMING.value, message_id='status-' + message_id).to_sse()
            client = OpenAI(base_url=self.model.base_url,
                            api_key=self.model.api_key)
            chat_messages = [chat_message(
                message) for message in messages]

            while True:
                yield StatusChunk(status=ChatStatus.STREAMING.value, message_id='status-' + message_id).to_sse()
                stream = client.chat.completions.create(
                    model=self.model.model,
                    messages=chat_messages,
                    stream=True,
                    tools=[tool.to_json() for tool in self.tools]
                )
                tc_id = None
                tc_name = None
                tc_args = ""
                finish_reason = None

                for _chunk in stream:
                    # 检查是否有工具调用
                    tool_calls_delta = _chunk.choices[0].delta.tool_calls or None
                    if tool_calls_delta:
                        tc = tool_calls_delta[0]
                        _tc_id = tc.id or None
                        _tc_name = tc.function.name or None
                        _tc_args = tc.function.arguments or None
                        if _tc_id:
                            tc_id = _tc_id
                        if _tc_name:
                            tc_name = _tc_name
                        if _tc_args:
                            tc_args += _tc_args
                    content = _chunk.choices[0].delta.content or None
                    if content:
                        yield ContentChunk(text=content, message_id='content-' + message_id).to_sse()
                    finish_reason = _chunk.choices[0].finish_reason or None
                    if finish_reason == "tool_calls":
                        break  # 工具调用参数全部流完，可以执行工具

                if not tc_name:
                    message_id = str(uuid.uuid4())
                    break

                # 执行所有工具调用
                if tc_name in [tool.name for tool in self.tools]:
                    tool = next(
                        tool for tool in self.tools if tool.name == tc_name)
                    yield StatusChunk(status=ChatStatus.TOOL_CALL.value, message_id='status-' + message_id).to_sse()
                    result = tool.call(tc_args)
                    messages.extend(tc_messages(
                        tc_id, tc_name, tc_args, result))
                    yield ContextChunk(text=result, message_id='context-' + message_id).to_sse()

        except Exception as e:
            yield ErrorChunk(text="Service Error: " + str(e), message_id='error-' + message_id).to_sse()
        finally:
            yield "data: [DONE]\n\n"
