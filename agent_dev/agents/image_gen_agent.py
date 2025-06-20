import uuid

from openai import OpenAI
from typing import List, AsyncIterator

from agent_dev.utils.s3 import b64_to_s3, S3
from agent_dev.agents.base import ChatStatus, ModelProvider
from agent_dev.stream.chunks import StatusChunk, ImageChunk, ErrorChunk
from agent_dev.stream.message import image_gen_message, Message


class ImageGenAgent:
    def __init__(self, model: ModelProvider, s3: S3):
        self.model = model
        self.s3 = s3

    async def stream(self, messages: List[Message]) -> AsyncIterator[str]:
        try:
            message_id = str(uuid.uuid4())

            yield StatusChunk(status=ChatStatus.STREAMING.value, message_id="status:" + message_id).to_sse()
            client = OpenAI(
                base_url=self.model.base_url, api_key=self.model.api_key)
            req = image_gen_message(messages[-1])
            if "image" in req:
                rsp = client.images.edit(
                    model=self.model.model,
                    prompt=req["prompt"],
                    image=req["image"],
                )
            else:
                rsp = client.images.generate(
                    model=self.model.model,
                    prompt=req["prompt"],
                )
            for data in rsp.data:
                if data.b64_json:
                    image_b64 = data.b64_json
                    file_url = b64_to_s3(image_b64, self.s3)
                    yield ImageChunk(image_url=file_url, message_id="image:" + message_id).to_sse()
        except Exception as e:
            yield ErrorChunk(text="Service Error: " + str(e), message_id="error:" + message_id).to_sse()
        finally:
            yield "data: [DONE]\n\n"
