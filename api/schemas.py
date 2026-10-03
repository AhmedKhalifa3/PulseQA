"""
Pydantic Schemas for API Response Contract Testing.
"""

from typing import List, Optional

from pydantic import BaseModel, Field


class LoginResponse(BaseModel):
    status: str
    token: str
    username: str


class ChatMessage(BaseModel):
    id: int
    user: str
    text: str
    timestamp: str
    audio: bool
    audio_url: str | None = None


class RoomMessagesResponse(BaseModel):
    room: str
    messages: list[ChatMessage]


class TTSResponse(BaseModel):
    status: str
    language: str
    sample_rate: int
    characters_processed: int
    duration_seconds: float
    audio_base64: str


class SystemHealthResponse(BaseModel):
    status: str
    cpu_percent: float
    memory_rss_mb: float
    threads: int
    timestamp: float
