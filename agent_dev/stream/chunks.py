from typing import Literal
from pydantic import BaseModel


class BaseChunk(BaseModel):
    message_id: str
    type: str

    def to_sse(self):
        return f"data: {self.model_dump_json()}\n\n"


class ContentChunk(BaseChunk):
    type: str = "content"
    text: str


class ReasoningChunk(BaseChunk):
    type: str = "reasoning"
    text: str


class ImageChunk(BaseChunk):
    type: str = "image"
    image_url: str


class ErrorChunk(BaseChunk):
    type: str = "error"
    text: str


class StatusChunk(BaseChunk):
    type: str = "status"
    status: Literal["idle", "streaming", "context-fetching", "tool-call"]


class ContextChunk(BaseChunk):
    type: str = "context"
    text: str


Chunk = ContentChunk | ReasoningChunk | ImageChunk | ErrorChunk | StatusChunk | ContextChunk
