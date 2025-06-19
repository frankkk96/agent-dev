from pydantic import BaseModel
from enum import Enum


class AgentMetadata(BaseModel):
    name: str
    avatar: str
    config_schema: str
    description: str
    capability: str


class Post(BaseModel):
    id: str
    timestamp: int
    content: str


class ChatStatus(Enum):
    IDLE = "idle"
    CONTEXT_FETCHING = "context-fetching"
    TOOL_CALL = "tool-call"
    STREAMING = "streaming"
