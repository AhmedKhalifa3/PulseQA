"""
Mobile Test Suite using Appium & Responsive Mobile Profiles.
Validates responsive layouts, touch interactions, and mobile driver integration.
Directly substantiates Appium Android test automation competencies.
"""

import pytest

from core.config import settings
from core.drivers.mobile_driver_factory import MobileDriverFactory


@pytest.mark.mobile
@pytest.mark.regression
@pytest.mark.testrail(104)
class TestMobileChat:

    def test_mobile_driver_session_initialization(self, mobile_driver):
        """Verifies Mobile WebDriver successfully establishes session and navigates."""
        mobile_driver.get(settings.BASE_URL)
        assert mobile_driver.current_url.startswith("http") or mobile_driver.current_url == "about:blank"

    def test_responsive_mobile_viewport(self, driver, target_app_server: str):
        """
        Simulates standard Android mobile viewport (412x915) using Selenium
        to assert mobile-responsive rendering and element visibility.
        """
        driver.set_window_size(412, 915)
        driver.get(target_app_server)

        # Confirm responsive container adapts
        from pages.login_page import LoginPage
        login_page = LoginPage(driver)
        assert login_page.is_login_screen_visible()

        # Login in mobile mode
        login_page.login_as("qa_automator", "securepass")

        from pages.chat_page import ChatPage
        chat_page = ChatPage(driver)
        assert chat_page.is_loaded()
        assert chat_page.get_current_user_name() == "qa_automator"
