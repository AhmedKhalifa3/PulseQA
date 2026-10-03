"""
Settings and Diagnostics Page Object for PulseChat.
"""

from core.locators.chat_locators import ChatLocators
from core.locators.settings_locators import SettingsLocators
from pages.base_page import BasePage


class SettingsPage(BasePage):
    """Page Object for diagnostics, stress controls, and system state."""

    def filter_channels(self, search_query: str) -> "SettingsPage":
        self.type_text(SettingsLocators.CHANNEL_SEARCH_INPUT, search_query)
        return self

    def is_telemetry_widget_active(self) -> bool:
        return self.is_displayed(SettingsLocators.TELEMETRY_WIDGET)
