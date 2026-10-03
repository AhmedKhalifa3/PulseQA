"""
Web UI Authentication Test Suite.
Tests login, invalid credential handling, and logout using Page Object Model.
"""

import allure
import pytest
from selenium.webdriver.remote.webdriver import WebDriver

from pages.chat_page import ChatPage
from pages.login_page import LoginPage


@allure.epic("PulseChat Web UI")
@allure.feature("Authentication & Session Lifecycle")
@pytest.mark.web
@pytest.mark.smoke
@pytest.mark.testrail(101)
class TestWebAuth:

    @allure.story("Valid User Login Navigation")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_successful_login(self, driver: WebDriver, target_app_server: str):
        """Verifies valid user credentials successfully navigate to main chat view."""
        login_page = LoginPage(driver)
        login_page.open(target_app_server)

        success = login_page.login_as("qa_automator", "securepass")
        assert success, "Expected main chat screen to be displayed after valid login"

        chat_page = ChatPage(driver)
        assert chat_page.get_current_user_name() == "qa_automator"

    def test_invalid_password_shows_error(self, driver: WebDriver, target_app_server: str):
        """Verifies invalid login displays validation error message."""
        login_page = LoginPage(driver)
        login_page.open(target_app_server)

        login_page.enter_username("qa_automator")
        login_page.enter_password("invalid_password_999")
        login_page.click_login()

        error_text = login_page.get_error_message()
        assert "Invalid username or password" in error_text

    def test_user_logout_flow(self, driver: WebDriver, target_app_server: str):
        """Verifies user can log out and is returned to the login card."""
        login_page = LoginPage(driver)
        login_page.open(target_app_server)
        login_page.login_as("alex", "pulse123")

        chat_page = ChatPage(driver)
        chat_page.logout()

        assert login_page.is_login_screen_visible()
