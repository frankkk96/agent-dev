import uuid

from openai import OpenAI
from typing import List, AsyncIterator

from utils.s3 import b64_to_s3, S3
from agents.base import ChatStatus

from stream.message import image_gen_message, Message
from stream.chunks import StatusChunk, ImageChunk


class ImageGenAgent:
    def __init__(self, base_url: str, api_key: str, model: str, s3: S3):
        self.base_url = base_url
        self.api_key = api_key
        self.model = model
        self.s3 = s3

    async def stream(self, req_messages: List[Message]) -> AsyncIterator[str]:
        try:
            message_id = str(uuid.uuid4())
            yield StatusChunk(status=ChatStatus.STREAMING.value, message_id="status:" + message_id).to_sse()
            client = OpenAI(
                base_url=self.base_url, api_key=self.api_key)
            req = image_gen_message(req_messages[-1])
            if "image" in req:
                rsp = client.images.edit(
                    model=self.model,
                    prompt=req["prompt"],
                    image=req["image"],
                )
            else:
                rsp = client.images.generate(
                    model=self.model,
                    prompt=req["prompt"],
                )
            for data in rsp.data:
                if data.b64_json:
                    image_b64 = data.b64_json
                    file_url = b64_to_s3(image_b64, self.s3)
                    yield ImageChunk(image_url=file_url, message_id="image:" + message_id).to_sse()
        except Exception as e:
            yield ImageChunk(image_url=None, error="Service Error: " + str(e), message_id="error:" + message_id).to_sse()
        finally:
            yield "data: [DONE]\n\n"
