"""
Web UI Multi-Channel Messaging & Real-Time Sync Test Suite.
"""

import time

import pytest
from selenium.webdriver.remote.webdriver import WebDriver

from pages.chat_page import ChatPage
from pages.login_page import LoginPage


@pytest.mark.web
@pytest.mark.regression
@pytest.mark.testrail(102)
class TestChatMessaging:
    @pytest.fixture(autouse=True)
    def setup_chat(self, driver: WebDriver, target_app_server: str):
        login_page = LoginPage(driver)
        login_page.open(target_app_server)
        login_page.login_as("qa_automator", "securepass")
        self.chat_page = ChatPage(driver)

    def test_switch_channels(self):
        """Verifies clicking different channels updates active channel viewport."""
        self.chat_page.switch_to_channel("qa-testing")
        assert self.chat_page.get_active_channel_title() == "qa-testing"

        self.chat_page.switch_to_channel("general")
        assert self.chat_page.get_active_channel_title() == "general"

    def test_send_and_receive_message(self):
        """Verifies sending a text message broadcasts and appends to message stream."""
        unique_text = f"Automated E2E Test Message [{time.time()}]"
        self.chat_page.switch_to_channel("qa-testing")
        self.chat_page.send_message(unique_text)

        messages = self.chat_page.get_all_message_texts()
        assert any(unique_text in msg for msg in messages), f"Message '{unique_text}' not found in {messages}"
