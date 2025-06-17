from typing import Literal

from pydantic import BaseModel


class ContentChunk(BaseModel):
    message_id: str
    type: str = "content"
    text: str


class ReasoningChunk(BaseModel):
    message_id: str
    type: str = "reasoning"
    text: str


class ImageChunk(BaseModel):
    message_id: str
    type: str = "image"
    image_url: str


class ErrorChunk(BaseModel):
    message_id: str
    type: str = "error"
    text: str


class StatusChunk(BaseModel):
    message_id: str
    type: str = "status"
    status: Literal["idle", "streaming", "context-fetching", "tool-call"]


class ContextChunk(BaseModel):
    message_id: str
    type: str = "context"
    text: str


Chunk = ContentChunk | ReasoningChunk | ImageChunk | ErrorChunk | StatusChunk | ContextChunk
