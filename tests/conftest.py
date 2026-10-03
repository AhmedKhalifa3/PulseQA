"""
Global Pytest Configuration and Fixtures for PulseQA.
Provides automated application server lifecycle, driver management,
telemetry capture, and TestRail reporting hooks.
"""

import logging
import os
import threading
import time
from typing import Any, Generator

import pytest
import requests
import uvicorn
from selenium.webdriver.remote.webdriver import WebDriver

from api.client import PulseApiClient
from core.config import settings
from core.drivers.mobile_driver_factory import MobileDriverFactory
from core.drivers.web_driver_factory import WebDriverFactory
from integrations.testrail.plugin import TestRailPytestPlugin
from target_app.app import app
from telemetry.monitor import ResourceMonitor, TelemetryResult
from telemetry.visualizer import TelemetryVisualizer

logger = logging.getLogger("PulseQA.Conftest")

# Global TestRail plugin instance
testrail_plugin = TestRailPytestPlugin()


def pytest_addoption(parser):
    parser.addoption(
        "--headed",
        action="store_true",
        default=False,
        help="Run browser in non-headless (headed / visible) mode"
    )
    parser.addoption(
        "--browser-name",
        action="store",
        default=None,
        help="Target browser: chrome or firefox"
    )


def pytest_configure(config):
    config.pluginmanager.register(testrail_plugin, name="pulseqa_testrail")


def get_free_port() -> int:
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture(scope="session", autouse=True)
def target_app_server():
    """
    Session fixture that ensures the PulseChat target application is running.
    Binds to an available port dynamically, starts Uvicorn, and updates settings.
    """
    port = get_free_port()
    base_url = f"http://127.0.0.1:{port}"
    settings.BASE_URL = base_url
    settings.WS_URL = f"ws://127.0.0.1:{port}"
    health_url = f"{base_url}/api/system/health"

    logger.info(f"Spawning background PulseChat target server on port {port}...")

    config = uvicorn.Config(app=app, host="127.0.0.1", port=port, log_level="warning")
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True, name="PulseChatServerThread")
    thread.start()

    # Wait for server readiness
    start_time = time.time()
    server_ready = False
    while time.time() - start_time < 10.0:
        try:
            res = requests.get(health_url, timeout=0.5)
            if res.status_code == 200:
                server_ready = True
                break
        except Exception:
            time.sleep(0.15)

    if not server_ready:
        raise RuntimeError(f"Failed to start background target app on port {port} within 10s")

    logger.info(f"Target application ready at {base_url}")
    yield base_url


@pytest.fixture
def api_client(target_app_server) -> Generator[PulseApiClient, None, None]:
    """Provides a fresh REST/WebSocket API client."""
    client = PulseApiClient(base_url=target_app_server)
    yield client
    client.close()


@pytest.fixture
def driver(request, target_app_server) -> Generator[WebDriver, None, None]:
    """
    Instantiates Selenium WebDriver with auto-teardown and screenshot-on-failure.
    Supports --headed CLI flag or HEADLESS=false environment variable.
    """
    headed_flag = request.config.getoption("--headed", default=False)
    browser_option = request.config.getoption("--browser-name", default=None)

    is_headless = False if headed_flag else settings.HEADLESS
    browser_driver = WebDriverFactory.create_driver(browser_name=browser_option, headless=is_headless)
    yield browser_driver

    # Capture failure screenshot
    if hasattr(request.node, "rep_call") and request.node.rep_call.failed:
        test_name = request.node.name
        screenshot_path = f"reports/screenshots/{test_name}.png"
        try:
            os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
            browser_driver.save_screenshot(screenshot_path)
            logger.info(f"Captured failure screenshot: {screenshot_path}")
            try:
                import allure
                allure.attach.file(
                    screenshot_path,
                    name=f"Failure Screenshot - {test_name}",
                    attachment_type=allure.attachment_type.PNG
                )
            except Exception:
                pass
        except Exception as e:
            logger.warning(f"Could not take screenshot: {e}")

    browser_driver.quit()


@pytest.fixture
def mobile_driver() -> Generator[Any, None, None]:
    """Provides an Appium Mobile Driver instance (with graceful mock fallback)."""
    mob_driver = MobileDriverFactory.create_driver()
    yield mob_driver
    mob_driver.quit()


@pytest.fixture
def telemetry_monitor(request) -> Generator[ResourceMonitor, None, None]:
    """
    Starts background process tree resource monitoring for CPU and RAM.
    On teardown, computes metrics summary and renders time-series chart.
    """
    test_name = request.node.name
    monitor = ResourceMonitor(interval_sec=settings.TELEMETRY_INTERVAL_SEC, test_name=test_name)
    monitor.start()

    yield monitor

    result = monitor.stop()
    request.node.telemetry_result = result

    # Render telemetry chart
    chart_path = TelemetryVisualizer.render_resource_chart(
        result=result,
        output_dir="reports/telemetry",
        max_cpu_threshold=settings.MAX_ALLOWED_CPU_PCT,
        max_ram_threshold=settings.MAX_ALLOWED_RAM_MB
    )
    logger.info(f"Telemetry report for {test_name}: {chart_path}")

    # Attach telemetry chart and metrics card to Allure
    try:
        import allure
        if chart_path and os.path.exists(chart_path):
            allure.attach.file(
                chart_path,
                name=f"Hardware Telemetry Curve - {test_name}",
                attachment_type=allure.attachment_type.PNG
            )
            summary_text = (
                f"Test: {result.test_name}\n"
                f"Duration: {result.duration_sec:.2f}s\n"
                f"Peak CPU: {result.peak_cpu_percent:.1f}%\n"
                f"Avg CPU: {result.avg_cpu_percent:.1f}%\n"
                f"Peak RAM: {result.peak_memory_rss_mb:.1f} MB\n"
                f"Memory Growth: {result.memory_growth_mb:+.1f} MB\n"
            )
            allure.attach(
                summary_text,
                name="Resource SLA Metrics Summary",
                attachment_type=allure.attachment_type.TEXT
            )
    except Exception:
        pass


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Stores test outcome on item for failure hooks."""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)
