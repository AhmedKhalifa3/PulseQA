"""
API System Stress & Telemetry Test Suite.
Verifies system health telemetry and controlled resource stress triggers.
"""

import pytest

from api.client import PulseApiClient
from api.schemas import SystemHealthResponse


@pytest.mark.api
@pytest.mark.regression
@pytest.mark.testrail(203)
class TestSystemStressApi:
    def test_system_health_telemetry_endpoint(self, api_client: PulseApiClient):
        """Validates system health telemetry API output."""
        res = api_client.get_health()
        assert res.status_code == 200

        data = res.json()
        model = SystemHealthResponse(**data)
        assert model.status == "healthy"
        assert model.memory_rss_mb > 0
        assert model.threads >= 1

    def test_controlled_memory_stress_and_cleanup(self, api_client: PulseApiClient):
        """Verifies memory allocation endpoint and subsequent cleanup cycle."""
        # Allocate 20MB
        res_alloc = api_client.stress_memory(memory_mb=20)
        assert res_alloc.status_code == 200
        assert res_alloc.json()["allocated_mb"] == 20

        # Reset memory
        res_reset = api_client.reset_memory()
        assert res_reset.status_code == 200
        assert res_reset.json()["current_chunks"] == 0
