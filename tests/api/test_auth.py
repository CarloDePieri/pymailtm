import pytest

from conftest import BASE_URL
from pymailtm.api.auth import AuthController
from pymailtm.api.credentials import Credentials
from pymailtm.api.connection_manager import ConnectionManagerWithRateLimiter


class TestAnAuthController:
    """Test: An Auth Controller..."""

    ac: AuthController

    @pytest.fixture(scope="class", autouse=True)
    def setup(self, request):
        """TestAnAccountController setup"""
        request.cls.ac = AuthController(ConnectionManagerWithRateLimiter())

    def test_should_be_able_to_authenticate(self, mock_api, mocks):
        """An auth controller should be able to authenticate."""
        mock_api.post(f"{BASE_URL}/token", json=mocks.json_token)
        credentials = Credentials(address="user@domain.test", password="password")
        token = self.ac.authenticate(credentials)
        assert token.token == mocks.token.token
