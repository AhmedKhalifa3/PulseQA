"""
WebDriver Factory supporting Chrome (with CDP Telemetry) and Firefox.
"""

import logging
import os
from typing import Optional

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService

from core.config import settings
from core.exceptions import DriverInitializationError

logger = logging.getLogger("PulseQA.WebDriverFactory")


class WebDriverFactory:
    """Produces configured Selenium WebDriver instances."""

    @staticmethod
    def create_driver(browser_name: str | None = None, headless: bool | None = None) -> webdriver.Remote:
        browser = (browser_name or settings.BROWSER).lower()
        is_headless = settings.HEADLESS if headless is None else headless

        logger.info(f"Initializing WebDriver for browser='{browser}' (headless={is_headless})")

        try:
            if browser == "chrome":
                return WebDriverFactory._create_chrome_driver(is_headless)
            elif browser == "firefox":
                return WebDriverFactory._create_firefox_driver(is_headless)
            else:
                raise DriverInitializationError(f"Unsupported browser: {browser}")
        except Exception as e:
            logger.warning(f"Failed to initialize '{browser}' ({e}). Attempting fallback...")
            # Fallback logic between Chrome and Firefox
            try:
                if browser == "chrome":
                    return WebDriverFactory._create_firefox_driver(is_headless)
                else:
                    return WebDriverFactory._create_chrome_driver(is_headless)
            except Exception as fallback_error:
                raise DriverInitializationError(
                    f"Failed to create both primary ('{browser}') and fallback drivers: {e} | Fallback: {fallback_error}"
                )

    @staticmethod
    def _create_chrome_driver(headless: bool) -> webdriver.Chrome:
        options = ChromeOptions()
        if headless:
            options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument(f"--window-size={settings.WINDOW_WIDTH},{settings.WINDOW_HEIGHT}")

        # Performance & CDP flags for resource telemetry
        options.set_capability("goog:loggingPrefs", {"performance": "ALL", "browser": "ALL"})

        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(settings.PAGE_LOAD_TIMEOUT)
        driver.implicitly_wait(settings.IMPLICIT_WAIT)
        return driver

    @staticmethod
    def _create_firefox_driver(headless: bool) -> webdriver.Firefox:
        options = FirefoxOptions()
        if headless:
            options.add_argument("-headless")
        options.add_argument(f"--width={settings.WINDOW_WIDTH}")
        options.add_argument(f"--height={settings.WINDOW_HEIGHT}")

        # Check for local geckodriver binary if available
        local_gecko = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../drivers/geckodriver"))
        service = FirefoxService(executable_path=local_gecko) if os.path.exists(local_gecko) else None

        driver = webdriver.Firefox(service=service, options=options) if service else webdriver.Firefox(options=options)
        driver.set_page_load_timeout(settings.PAGE_LOAD_TIMEOUT)
        driver.implicitly_wait(settings.IMPLICIT_WAIT)
        return driver
