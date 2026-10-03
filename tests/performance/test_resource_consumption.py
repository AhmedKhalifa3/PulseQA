"""
Performance & Resource Consumption Verification Suite.
Demonstrates real-time hardware telemetry (CPU, RAM, JS Heap) tracking and threshold assertions.
Directly substantiates the Resource Consumption Framework concept-to-deployment achievement.
"""

import time

import allure
import pytest
from selenium.webdriver.remote.webdriver import WebDriver

from core.exceptions import ResourceThresholdExceededError
from pages.chat_page import ChatPage
from pages.login_page import LoginPage
from telemetry.cdp_metrics import CDPMetricsExtractor
from telemetry.thresholds import assert_resource_limits


@allure.epic("PulseQA Hardware Telemetry")
@allure.feature("Browser Resource Profiling & SLA Assertions")
@pytest.mark.performance
@pytest.mark.regression
@pytest.mark.testrail(105)
class TestResourceConsumption:

    @allure.story("Continuous Browser CPU & RAM Tracking")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_chat_workflow_resource_limits(self, driver: WebDriver, target_app_server: str, telemetry_monitor, request):
        """
        Executes an intensive chat session while continuous background telemetry monitors
        hardware usage. Asserts that browser CPU % and RAM stay well below maximum limits.
        """
        login_page = LoginPage(driver)
        login_page.open(target_app_server)
        login_page.login_as("qa_automator", "securepass")

        chat_page = ChatPage(driver)

        # Simulate active chat session
        for i in range(5):
            chat_page.send_message(f"Automated stress iteration #{i}")
            time.sleep(0.15)

        chat_page.switch_to_channel("qa-testing")
        chat_page.send_message("Testing channel switch memory stability")

        # Telemetry teardown runs after this test, but we can also manually assert on collected samples
        # Stop monitor to grab result for in-test assertion
        result = telemetry_monitor.stop()
        assert len(result.samples) > 0, "Expected telemetry samples to be collected during test"

        # Assert resource limits (Multi-core process tree: max 85% average CPU, max 250% peak burst, max 1500MB RAM)
        assert_resource_limits(
            result,
            max_avg_cpu_pct=85.0,
            max_cpu_pct=250.0,
            max_ram_mb=1500.0
        )

    def test_cdp_internal_heap_metrics(self, driver: WebDriver, target_app_server: str):
        """
        Directly queries the Chrome DevTools Protocol (CDP) for internal V8 JS Heap size
        and DOM node count during page lifecycle.
        """
        login_page = LoginPage(driver)
        login_page.open(target_app_server)
        login_page.login_as("alex", "pulse123")

        extractor = CDPMetricsExtractor(driver)
        metrics = extractor.get_browser_metrics()

        if metrics.get("supported"):
            assert metrics["js_heap_used_mb"] > 0
            assert metrics["dom_nodes"] > 0
            assert metrics["layout_count"] >= 0
            print(f"\n[CDP Telemetry] JS Heap Used: {metrics['js_heap_used_mb']} MB, DOM Nodes: {metrics['dom_nodes']}")
        else:
            pytest.skip("CDP not supported by current browser driver engine (e.g. Firefox)")

    def test_threshold_violation_detection(self, telemetry_monitor):
        """
        Validates that the framework successfully flags when a configured SLA limit is breached.
        """
        time.sleep(0.5)
        result = telemetry_monitor.stop()

        # Artificially test threshold enforcement with a strict 0.001MB limit
        with pytest.raises(ResourceThresholdExceededError) as exc_info:
            assert_resource_limits(result, max_ram_mb=0.001)

        assert "Resource threshold breached" in str(exc_info.value)
