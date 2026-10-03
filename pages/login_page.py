"""
Login Page Object encapsulating authentication flows.
"""

from typing import Optional

from core.locators.chat_locators import ChatLocators
from core.locators.login_locators import LoginLocators
from pages.base_page import BasePage


class LoginPage(BasePage):
    """Page Object for PulseChat Login Screen."""

    def open(self, base_url: str) -> "LoginPage":
        self.navigate_to(base_url)
        self.wait_for_element_visible(LoginLocators.AUTH_SCREEN)
        return self

    def enter_username(self, username: str) -> "LoginPage":
        self.type_text(LoginLocators.USERNAME_INPUT, username)
        return self

    def enter_password(self, password: str) -> "LoginPage":
        self.type_text(LoginLocators.PASSWORD_INPUT, password)
        return self

    def click_login(self):
        self.click(LoginLocators.LOGIN_BUTTON)

    def login_as(self, username: str, password: str) -> bool:
        """Executes full login and asserts navigation to main chat screen."""
        self.enter_username(username)
        self.enter_password(password)
        self.click_login()
        return self.is_displayed(ChatLocators.MAIN_SCREEN, timeout=8)

    def get_error_message(self) -> str:
        return self.get_text(LoginLocators.LOGIN_ERROR)

    def is_login_screen_visible(self) -> bool:
        return self.is_displayed(LoginLocators.AUTH_SCREEN)
