from typing import Literal

from pydantic import BaseModel


class ContentChunk(BaseModel):
    type: str = "content"
    text: str


class ReasoningChunk(BaseModel):
    type: str = "reasoning"
    text: str


class ImageChunk(BaseModel):
    type: str = "image"
    image_url: str


class ErrorChunk(BaseModel):
    type: str = "error"
    text: str


class StatusChunk(BaseModel):
    type: str = "status"
    status: Literal["idle", "streaming", "context-fetching", "tool-call"]


class ContextChunk(BaseModel):
    type: str = "context"
    text: str


class EndStreamChunk(BaseModel):
    type: str = "end_stream"
