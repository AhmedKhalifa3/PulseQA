"""
Centralized Configuration Manager for PulseQA.
Supports .env overrides, CLI overrides, and enterprise defaults.
"""

from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Environment & Target URL
    ENV: str = Field(default="local", description="Environment: local, staging, prod")
    BASE_URL: str = Field(default="http://127.0.0.1:8000", description="Base application URL")
    WS_URL: str = Field(default="ws://127.0.0.1:8000", description="Base WebSocket URL")

    # Browser & UI Automation
    BROWSER: str = Field(default="chrome", description="Browser: chrome, firefox")
    HEADLESS: bool = Field(default=True, description="Run browser in headless mode")
    IMPLICIT_WAIT: int = Field(default=5, description="Implicit wait timeout in seconds")
    EXPLICIT_WAIT: int = Field(default=10, description="Explicit wait timeout in seconds")
    PAGE_LOAD_TIMEOUT: int = Field(default=30, description="Page load timeout in seconds")
    WINDOW_WIDTH: int = Field(default=1920, description="Browser window width")
    WINDOW_HEIGHT: int = Field(default=1080, description="Browser window height")

    # Mobile Automation (Appium)
    APPIUM_SERVER_URL: str = Field(default="http://127.0.0.1:4723", description="Appium server URL")
    DEVICE_NAME: str = Field(default="Android Emulator", description="Target mobile device name")
    PLATFORM_VERSION: str = Field(default="14.0", description="Android OS version")
    MOBILE_BROWSER: str = Field(default="Chrome", description="Mobile browser or native app package")

    # Telemetry & Resource Consumption
    ENABLE_RESOURCE_MONITORING: bool = Field(default=True, description="Enable CPU & RAM telemetry")
    TELEMETRY_INTERVAL_SEC: float = Field(default=0.2, description="Sampling interval in seconds")
    MAX_ALLOWED_RAM_MB: float = Field(default=350.0, description="Default max RAM limit in MB")
    MAX_ALLOWED_CPU_PCT: float = Field(default=90.0, description="Default max CPU limit in %")

    # Test Management (TestRail)
    TESTRAIL_ENABLED: bool = Field(default=False, description="Enable TestRail reporting")
    TESTRAIL_MOCK_MODE: bool = Field(default=True, description="Enable standalone mock mode for TestRail")
    TESTRAIL_URL: str = Field(default="https://pulseqa.testrail.io", description="TestRail URL")
    TESTRAIL_USER: str = Field(default="qa_automator@pulseqa.local", description="TestRail username")
    TESTRAIL_API_KEY: str = Field(default="mock_api_key_12345", description="TestRail API key")
    TESTRAIL_PROJECT_ID: int = Field(default=1, description="TestRail Project ID")
    TESTRAIL_SUITE_ID: int = Field(default=101, description="TestRail Suite ID")


settings = Settings()
