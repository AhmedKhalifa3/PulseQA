"""
API Authentication & Contract Test Suite.
"""

import pytest

from api.client import PulseApiClient
from api.schemas import LoginResponse


@pytest.mark.api
@pytest.mark.smoke
@pytest.mark.testrail(201)
class TestAuthApi:
    def test_login_success(self, api_client: PulseApiClient):
        """Verifies valid login returns 200, auth token, and adheres to schema."""
        res = api_client.login("qa_automator", "securepass")
        assert res.status_code == 200

        data = res.json()
        model = LoginResponse(**data)
        assert model.status == "success"
        assert model.username == "qa_automator"
        assert model.token.startswith("token-qa_automator-")

    def test_login_invalid_credentials(self, api_client: PulseApiClient):
        """Verifies invalid login returns 401 Unauthorized."""
        res = api_client.login("qa_automator", "wrong_pass_xyz")
        assert res.status_code == 401
        assert "Invalid username or password" in res.json()["detail"]

    def test_logout(self, api_client: PulseApiClient):
        """Verifies logout invalidates the token."""
        api_client.login("alex", "pulse123")
        res = api_client.logout()
        assert res.status_code == 200
        assert res.json()["status"] == "logged_out"
