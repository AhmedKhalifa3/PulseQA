"""
Pytest Plugin for TestRail test run synchronization.
Maps @pytest.mark.testrail(case_id=...) to TestRail execution results.
"""

import logging
import time
from typing import Any, Dict, List, Optional

import pytest

from core.config import settings
from integrations.testrail.client import TestRailClient

logger = logging.getLogger("PulseQA.TestRailPlugin")


class TestRailPytestPlugin:
    """Hooks into Pytest lifecycle to sync results to TestRail."""

    def __init__(self, client: TestRailClient | None = None):
        self.client = client or TestRailClient()
        self.run_id: int | None = None
        self.results_queue: list[dict[str, Any]] = []

    def pytest_configure(self, config):
        if settings.TESTRAIL_ENABLED:
            run_name = f"PulseQA Automated Regression - {time.strftime('%Y-%m-%d %H:%M')}"
            try:
                self.run_id = self.client.create_run(
                    project_id=settings.TESTRAIL_PROJECT_ID,
                    suite_id=settings.TESTRAIL_SUITE_ID,
                    name=run_name,
                    description="Executed automatically by PulseQA CI/CD test runner."
                )
                logger.info(f"TestRail integration initialized. Run ID: {self.run_id}")
            except Exception as e:
                logger.error(f"Failed to initialize TestRail run: {e}")

    @pytest.hookimpl(tryfirst=True, hookwrapper=True)
    def pytest_runtest_makereport(self, item, call):
        outcome = yield
        report = outcome.get_result()

        # Only process on call phase (actual test run)
        if report.when == "call" and settings.TESTRAIL_ENABLED:
            marker = item.get_closest_marker("testrail")
            if marker:
                case_id = marker.kwargs.get("id") or (marker.args[0] if marker.args else None)
                if case_id:
                    status_id = TestRailClient.STATUS_PASSED if report.passed else TestRailClient.STATUS_FAILED
                    comment = f"Executed in {report.duration:.2f}s"
                    if report.failed:
                        comment += f"\nFailure: {report.longreprtext[:300]}"

                    self.results_queue.append({
                        "case_id": int(case_id),
                        "status_id": status_id,
                        "elapsed": f"{max(int(report.duration), 1)}s",
                        "comment": comment
                    })

    def pytest_sessionfinish(self, session, exitstatus):
        if settings.TESTRAIL_ENABLED and self.run_id and self.results_queue:
            try:
                self.client.add_results_for_cases(self.run_id, self.results_queue)
                logger.info(f"Successfully uploaded {len(self.results_queue)} test results to TestRail Run #{self.run_id}")
            except Exception as e:
                logger.error(f"Failed uploading TestRail results: {e}")
