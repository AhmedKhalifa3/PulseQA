"""
TestRail v2 API Client with live authentication and zero-dependency mock modes.
Directly substantiates enterprise test management tracking competencies.
"""

import logging
import time
from typing import Any, Dict, List, Optional

import requests
from requests.auth import HTTPBasicAuth

from core.config import settings
from core.exceptions import TestRailSyncError

logger = logging.getLogger("PulseQA.TestRail")


class TestRailClient:
    """TestRail API v2 Client."""

    # TestRail Status IDs
    STATUS_PASSED = 1
    STATUS_BLOCKED = 2
    STATUS_UNTESTED = 3
    STATUS_RETEST = 4
    STATUS_FAILED = 5

    def __init__(
        self,
        base_url: str | None = None,
        user: str | None = None,
        api_key: str | None = None,
        mock_mode: bool | None = None,
    ):
        self.base_url = (base_url or settings.TESTRAIL_URL).rstrip("/")
        self.user = user or settings.TESTRAIL_USER
        self.api_key = api_key or settings.TESTRAIL_API_KEY
        self.mock_mode = settings.TESTRAIL_MOCK_MODE if mock_mode is None else mock_mode
        self.session = requests.Session()
        self.session.auth = HTTPBasicAuth(self.user, self.api_key)
        self.session.headers.update({"Content-Type": "application/json"})

        # In-memory store for mock execution runs
        self.mock_runs: dict[int, dict[str, Any]] = {}
        self.mock_results: list[dict[str, Any]] = []

    def create_run(self, project_id: int, suite_id: int, name: str, description: str = "") -> int:
        """Creates a new test run in TestRail."""
        if self.mock_mode:
            mock_run_id = int(time.time()) % 100000
            self.mock_runs[mock_run_id] = {
                "id": mock_run_id,
                "project_id": project_id,
                "suite_id": suite_id,
                "name": name,
                "description": description,
                "created_on": time.time(),
            }
            logger.info(f"[TestRail Mock] Created run ID #{mock_run_id}: '{name}'")
            return mock_run_id

        url = f"{self.base_url}/index.php?/api/v2/add_run/{project_id}"
        payload = {"suite_id": suite_id, "name": name, "description": description, "include_all": True}
        res = self.session.post(url, json=payload)
        if res.status_code != 200:
            raise TestRailSyncError(f"Failed to create TestRail run: {res.status_code} - {res.text}")
        return res.json()["id"]

    def add_results_for_cases(self, run_id: int, results: list[dict[str, Any]]) -> bool:
        """Batch publishes test results for multiple test cases."""
        if not results:
            return True

        if self.mock_mode:
            for item in results:
                self.mock_results.append({"run_id": run_id, **item})
            logger.info(f"[TestRail Mock] Published {len(results)} case results to Run #{run_id}")
            return True

        url = f"{self.base_url}/index.php?/api/v2/add_results_for_cases/{run_id}"
        payload = {"results": results}
        res = self.session.post(url, json=payload)
        if res.status_code != 200:
            raise TestRailSyncError(f"Failed to post results to TestRail: {res.status_code} - {res.text}")
        return True

    def close_run(self, run_id: int) -> bool:
        """Closes the test run in TestRail."""
        if self.mock_mode:
            if run_id in self.mock_runs:
                self.mock_runs[run_id]["is_completed"] = True
            logger.info(f"[TestRail Mock] Closed Run #{run_id}")
            return True

        url = f"{self.base_url}/index.php?/api/v2/close_run/{run_id}"
        res = self.session.post(url)
        return res.status_code == 200
