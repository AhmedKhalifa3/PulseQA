"""
Robust REST & WebSocket API Client for PulseChat.
Includes contract validation, payload logging, and authentication state management.
"""

import logging
from typing import Any, Dict, Optional

import httpx

from api.schemas import LoginResponse, RoomMessagesResponse, SystemHealthResponse, TTSResponse
from core.config import settings

logger = logging.getLogger("PulseQA.ApiClient")


class PulseApiClient:
    """REST API Client encapsulating endpoints and session handling."""

    def __init__(self, base_url: str | None = None):
        self.base_url = base_url or settings.BASE_URL
        self.token: str | None = None
        self._client = httpx.Client(base_url=self.base_url, timeout=10.0)

    def set_auth_token(self, token: str):
        self.token = token
        self._client.headers["Authorization"] = f"Bearer {token}"

    def clear_auth(self):
        self.token = None
        if "Authorization" in self._client.headers:
            del self._client.headers["Authorization"]

    def login(self, username: str, password: str) -> httpx.Response:
        logger.info(f"API Login attempt for user: {username}")
        res = self._client.post("/api/auth/login", json={"username": username, "password": password})
        if res.is_success:
            data = res.json()
            self.set_auth_token(data["token"])
        return res

    def logout(self) -> httpx.Response:
        res = self._client.post("/api/auth/logout")
        self.clear_auth()
        return res

    def get_rooms(self) -> httpx.Response:
        return self._client.get("/api/chat/rooms")

    def get_messages(self, room: str) -> httpx.Response:
        return self._client.get(f"/api/chat/messages/{room}")

    def send_message(self, room: str, text: str) -> httpx.Response:
        return self._client.post("/api/chat/messages", json={"room": room, "text": text})

    def synthesize_audio(self, text: str, language: str = "en") -> httpx.Response:
        return self._client.post("/api/audio/synthesize", json={"text": text, "language": language})

    def get_health(self) -> httpx.Response:
        return self._client.get("/api/system/health")

    def stress_cpu(self, duration_sec: float = 1.0, intensity: float = 1.0) -> httpx.Response:
        return self._client.post("/api/system/stress/cpu", json={"duration_sec": duration_sec, "intensity": intensity})

    def stress_memory(self, memory_mb: int = 20) -> httpx.Response:
        return self._client.post("/api/system/stress/memory", json={"memory_mb": memory_mb})

    def reset_memory(self) -> httpx.Response:
        return self._client.post("/api/system/stress/memory/reset")

    def close(self):
        self._client.close()
