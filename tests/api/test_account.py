import pytest

from conftest import BASE_URL

from pymailtm.api.account import AccountController
from pymailtm.api.credentials import Credentials
from pymailtm.api.connection_manager import ConnectionManager


class TestAnAccountController:
    """Test: An Account Controller..."""

    ac: AccountController

    @pytest.fixture(scope="class", autouse=True)
    def setup(self, request):
        """TestAnAccountController setup"""
        request.cls.ac = AccountController(ConnectionManager(BASE_URL))

    def test_should_be_able_to_create_a_new_account(self, mock_api, mocks):
        """An account controller should be able to create a new account."""
        # set up the api mock
        mock_api.post(f"{BASE_URL}/accounts", json=mocks.json_account)
        credentials = Credentials(address="user@domain.test", password="password")

        # create a new account
        account = self.ac.create_account(credentials)
        assert account == mocks.account
        assert credentials.address
        assert credentials.password
