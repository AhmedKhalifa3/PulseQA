"""
Web UI Audio Note & Speech Synthesis (TTS) Test Suite.
Validates the end-to-end user experience for audio note generation and playback rendering.
"""

import time

import pytest
from selenium.webdriver.remote.webdriver import WebDriver

from pages.chat_page import ChatPage
from pages.login_page import LoginPage


@pytest.mark.web
@pytest.mark.regression
@pytest.mark.testrail(103)
class TestMediaPlayback:

    def test_synthesize_and_render_audio_note(self, driver: WebDriver, target_app_server: str):
        """
        Verifies opening the TTS modal, generating speech, and asserting audio player element.
        Directly reflects real-time audio pipeline verification.
        """
        login_page = LoginPage(driver)
        login_page.open(target_app_server)
        login_page.login_as("sarah", "pulse123")

        chat_page = ChatPage(driver)
        chat_page.switch_to_channel("media-tts")

        initial_players = chat_page.get_audio_players_count()
        chat_page.synthesize_and_send_audio(
            script_text="PulseQA automated speech note playback test.",
            language="de"
        )

        # Confirm new audio player element is present in message history
        new_players = chat_page.get_audio_players_count()
        assert new_players >= initial_players + 1, "Expected audio player element to be added to chat viewport"
