"""
Pydantic Schemas for API Response Contract Testing.
"""

from pydantic import BaseModel


class LoginResponse(BaseModel):
    status: str
    token: str
    username: str


class ChatMessage(BaseModel):
    id: int
    user: str
    text: str
    timestamp: str


class RoomMessagesResponse(BaseModel):
    room: str
    messages: list[ChatMessage]


class SystemHealthResponse(BaseModel):
    status: str
    cpu_percent: float
    memory_rss_mb: float
    threads: int
    timestamp: float
