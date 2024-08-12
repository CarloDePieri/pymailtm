import pytest

from pymailtm.api.connection_manager import ConnectionManager
from pymailtm.api.message import MessageController
from conftest import BASE_URL


class TestAMessageController:
    """Test: A Message Controller..."""

    message_controller = MessageController

    @pytest.fixture(scope="class", autouse=True)
    def setup(self, request):
        """TestAMessageController setup"""
        request.cls.message_controller = MessageController(ConnectionManager(BASE_URL))

    def test_should_be_able_to_download_a_messages_page(
        self, mock_api, mocks, auth_response_callback
    ):
        """A message controller should be able to download a messages page."""
        mock_api.get(
            f"{BASE_URL}/messages?page=1",
            status_code=200,
            json=auth_response_callback(
                mocks.token, mocks.json_messages_page_1, status_code=200
            ),
        )
        message_page = self.message_controller.get_messages_page(mocks.token)
        assert message_page.hydra_member == [
            mocks.message,
            mocks.message,
            mocks.message,
        ]
