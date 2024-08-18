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
        request.cls.ac = AccountController(ConnectionManager())

    def test_should_be_able_to_create_a_new_account(self, mock_api, mocks):
        """An account controller should be able to create a new account."""
        # set up the api mock
        mock_api.post(f"{BASE_URL}/accounts", json=mocks.json_new_account)
        credentials = Credentials(address="user@domain.test", password="password")

        # create a new account
        account = self.ac.create_account(credentials)
        assert account == mocks.account
        assert credentials.address
        assert credentials.password

    def test_should_be_able_to_get_account_info(
        self, mock_api, mocks, auth_response_callback
    ):
        """An account controller should be able to get account info."""
        # set up the api mock
        mock_api.get(
            f"{BASE_URL}/accounts/{mocks.account.id}",
            json=auth_response_callback(mocks.token, mocks.json_account),
        )

        # get account info
        account = self.ac.get_account_by_id(mocks.account.id, mocks.token)
        assert account == mocks.account

    def test_should_be_able_to_get_me_info(
        self, mock_api, mocks, auth_response_callback
    ):
        """An account controller should be able to get /me info."""
        # set up the api mock
        mock_api.get(
            f"{BASE_URL}/me",
            json=auth_response_callback(mocks.token, mocks.json_me),
        )

        # get me info
        account = self.ac.get_me(mocks.token)
        assert account == mocks.account

    def test_should_be_able_to_delete_an_account(
        self, mock_api, mocks, auth_response_callback
    ):
        """An account controller should be able to delete an account."""
        mock_api.delete(
            f"{BASE_URL}/accounts/{mocks.account.id}",
            json=auth_response_callback(mocks.token, "", status_code=204),
        )

        result = self.ac.delete_account(mocks.account.id, mocks.token)
        assert result
