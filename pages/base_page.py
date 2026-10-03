"""
Base Page implementing Page Object Model patterns, explicit wait synchronization,
and automatic diagnostic reporting.
"""

import logging
import os
import time
from typing import List, Optional, Tuple

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from core.config import settings
from core.exceptions import ElementTimeoutException

logger = logging.getLogger("PulseQA.POM")


class BasePage:
    """Base class for all Page Objects with robust explicit waiting."""

    def __init__(self, driver: WebDriver, timeout: int | None = None):
        self.driver = driver
        self.timeout = timeout or settings.EXPLICIT_WAIT
        self.wait = WebDriverWait(self.driver, self.timeout)

    def navigate_to(self, url: str):
        logger.info(f"Navigating to: {url}")
        self.driver.get(url)

    def wait_for_element_visible(self, locator: tuple[str, str], timeout: int | None = None) -> WebElement:
        wait = WebDriverWait(self.driver, timeout or self.timeout)
        try:
            return wait.until(EC.visibility_of_element_located(locator))
        except TimeoutException:
            raise ElementTimeoutException(f"Timed out waiting for element {locator} to become visible after {timeout or self.timeout}s")

    def wait_for_element_clickable(self, locator: tuple[str, str], timeout: int | None = None) -> WebElement:
        wait = WebDriverWait(self.driver, timeout or self.timeout)
        try:
            return wait.until(EC.element_to_be_clickable(locator))
        except TimeoutException:
            raise ElementTimeoutException(f"Timed out waiting for element {locator} to be clickable after {timeout or self.timeout}s")

    def wait_for_element_invisible(self, locator: tuple[str, str], timeout: int | None = None) -> bool:
        wait = WebDriverWait(self.driver, timeout or self.timeout)
        try:
            return wait.until(EC.invisibility_of_element_located(locator))
        except TimeoutException:
            return False

    def find(self, locator: tuple[str, str]) -> WebElement:
        return self.wait_for_element_visible(locator)

    def find_all(self, locator: tuple[str, str]) -> list[WebElement]:
        try:
            self.wait_for_element_visible(locator)
            return self.driver.find_elements(*locator)
        except ElementTimeoutException:
            return []

    def click(self, locator: tuple[str, str]):
        element = self.wait_for_element_clickable(locator)
        element.click()
        logger.debug(f"Clicked on element: {locator}")

    def type_text(self, locator: tuple[str, str], text: str, clear_first: bool = True):
        element = self.wait_for_element_visible(locator)
        if clear_first:
            element.clear()
        element.send_keys(text)
        logger.debug(f"Typed text into: {locator}")

    def get_text(self, locator: tuple[str, str]) -> str:
        element = self.wait_for_element_visible(locator)
        return element.text.strip()

    def is_displayed(self, locator: tuple[str, str], timeout: int = 3) -> bool:
        try:
            self.wait_for_element_visible(locator, timeout=timeout)
            return True
        except ElementTimeoutException:
            return False

    def take_screenshot(self, filepath: str) -> str:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        self.driver.save_screenshot(filepath)
        logger.info(f"Saved screenshot to: {filepath}")
        return filepath
