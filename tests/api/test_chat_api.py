"""
API Messaging & Room Retrieval Test Suite.
"""

import pytest

from api.client import PulseApiClient
from api.schemas import RoomMessagesResponse


@pytest.mark.api
@pytest.mark.regression
@pytest.mark.testrail(202)
class TestChatApi:
    def test_get_rooms(self, api_client: PulseApiClient):
        """Verifies room discovery returns default configured rooms."""
        res = api_client.get_rooms()
        assert res.status_code == 200
        rooms = res.json()["rooms"]
        assert "general" in rooms
        assert "qa-testing" in rooms

    def test_get_messages_contract(self, api_client: PulseApiClient):
        """Validates room message payload against Pydantic schema."""
        res = api_client.get_messages("general")
        assert res.status_code == 200
        data = res.json()
        model = RoomMessagesResponse(**data)
        assert model.room == "general"
        assert len(model.messages) >= 1

    def test_post_message_authenticated(self, api_client: PulseApiClient):
        """Verifies authenticated user can post to channel."""
        api_client.login("qa_automator", "securepass")
        text_payload = "Automated API verification message"
        res = api_client.send_message("qa-testing", text_payload)

        assert res.status_code == 200
        sent_msg = res.json()["message"]
        assert sent_msg["user"] == "qa_automator"
        assert sent_msg["text"] == text_payload
