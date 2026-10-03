"""
Chat Page Object encapsulating multi-channel communication,
real-time messaging interactions, and diagnostic controls.
"""

import time

from core.locators.chat_locators import ChatLocators
from core.locators.login_locators import LoginLocators
from pages.base_page import BasePage


class ChatPage(BasePage):
    """Page Object for PulseChat Main Viewport & Channels."""

    def is_loaded(self) -> bool:
        return self.is_displayed(ChatLocators.MAIN_SCREEN)

    def get_current_user_name(self) -> str:
        return self.get_text(ChatLocators.CURRENT_USER_NAME)

    def switch_to_channel(self, channel_name: str) -> "ChatPage":
        channel_name_clean = channel_name.replace("#", "").strip()
        if channel_name_clean == "general":
            self.click(ChatLocators.CHANNEL_GENERAL)
        elif channel_name_clean == "qa-testing":
            self.click(ChatLocators.CHANNEL_QA_TESTING)
        else:
            raise ValueError(f"Unknown channel: {channel_name}")

        # Verify active channel header updates
        time.sleep(0.3)
        return self

    def get_active_channel_title(self) -> str:
        return self.get_text(ChatLocators.ACTIVE_CHANNEL_NAME)

    def send_message(self, text: str) -> "ChatPage":
        self.type_text(ChatLocators.MESSAGE_INPUT, text)
        self.click(ChatLocators.SEND_BUTTON)
        time.sleep(0.4)  # brief sync for WebSocket broadcast
        return self

    def get_all_message_texts(self) -> list[str]:
        items = self.find_all(ChatLocators.ALL_MESSAGES)
        return [item.text for item in items]

    def toggle_stress_drawer(self) -> "ChatPage":
        self.click(ChatLocators.STRESS_TOGGLE_BUTTON)
        return self

    def trigger_cpu_stress(self) -> "ChatPage":
        if not self.is_displayed(ChatLocators.STRESS_DRAWER):
            self.toggle_stress_drawer()
        self.click(ChatLocators.STRESS_CPU_BUTTON)
        return self

    def trigger_memory_stress(self) -> "ChatPage":
        if not self.is_displayed(ChatLocators.STRESS_DRAWER):
            self.toggle_stress_drawer()
        self.click(ChatLocators.STRESS_MEM_BUTTON)
        return self

    def reset_stress_memory(self) -> "ChatPage":
        if not self.is_displayed(ChatLocators.STRESS_DRAWER):
            self.toggle_stress_drawer()
        self.click(ChatLocators.STRESS_RESET_BUTTON)
        return self

    def get_telemetry_badge_metrics(self) -> tuple[str, str]:
        cpu_text = self.get_text(ChatLocators.METRIC_CPU)
        ram_text = self.get_text(ChatLocators.METRIC_RAM)
        return cpu_text, ram_text

    def logout(self):
        self.click(ChatLocators.LOGOUT_BUTTON)
        self.wait_for_element_visible(LoginLocators.AUTH_SCREEN)
