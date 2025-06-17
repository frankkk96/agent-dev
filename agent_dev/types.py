from enum import Enum
from pydantic import BaseModel
from typing import Optional


class ChatStatus(Enum):
    IDLE = "idle"
    CONTEXT_FETCHING = "context-fetching"
    TOOL_CALL = "tool-call"
    STREAMING = "streaming"


class Agent(BaseModel):
    name: str
    avatar: str
    config_schema: str


class Post(BaseModel):
    id: str
    timestamp: int
    content: str


class Message(BaseModel):
    role: str
    text: str
    image_url: Optional[str] = None
