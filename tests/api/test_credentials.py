import pytest

from conftest import BASE_URL

from pymailtm.api.credentials import CredentialsController
from pymailtm.api.connection_manager import ConnectionManager
from pymailtm.api.domain import DomainController
from pymailtm.api.utils import MailTmAPIException


class TestACredentialsController:
    """Test: A Credentials Controller..."""

    cm: CredentialsController

    @pytest.fixture(scope="class", autouse=True)
    def setup(self, request):
        """TestACredentialsController setup"""
        domain_controller = DomainController(ConnectionManager())
        request.cls.cm = CredentialsController(domain_controller)

    def test_should_be_able_to_create_a_set_of_credentials(self, mock_api, mocks):
        """A credentials controller should be able to create a set of credentials."""
        # set up the api mock
        mock_api.get(f"{BASE_URL}/domains", json=mocks.json_domains)
        credentials = self.cm.generate()
        assert credentials.address.endswith(f"@{mocks.domain.domain}")
        assert credentials.password

    def test_should_be_able_to_create_credentials_while_specifying_parts_of_it(
        self, mock_api, mocks
    ):
        """A credentials controller should be able to create credentials while specifying parts of it."""
        # set up the api mock
        mock_api.get(f"{BASE_URL}/domains", json=mocks.json_domains)
        username = "username"
        password = "password"
        credentials = self.cm.generate(username=username, password=password)
        assert credentials.address == f"{username}@{mocks.domain.domain}"
        assert credentials.password == password

    def test_should_raise_when_generating_an_user_with_no_available_domain(
        self, mock_api, mocks
    ):
        """A credentials controller should raise when generating a user with no available domain."""
        mock_api.get(f"{BASE_URL}/domains", json=mocks.json_empty_domains)
        with pytest.raises(MailTmAPIException):
            self.cm.generate()
