from typing import Callable

import pytest

from pymailtm.api.auth import Token
from pymailtm.api.connection_manager import ConnectionManager
from pymailtm.api.message import MessageController
from conftest import BASE_URL


class TestAMessageController:
    """Test: A Message Controller..."""

    get_controller: Callable[[Token], MessageController]

    @pytest.fixture(scope="class", autouse=True)
    def setup(self, request):
        """TestAMessageController setup"""
        request.cls.get_controller = lambda _, token: MessageController(
            ConnectionManager(BASE_URL), token
        )

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
        message_page = self.get_controller(mocks.token).get_message_intros_page()
        assert message_page.hydra_member == [
            mocks.message_intro,
            mocks.message_intro,
            mocks.message_intro,
        ]

    def test_should_be_able_to_return_the_total_message_count(
        self, mock_api, mocks, auth_response_callback
    ):
        """A message controller should be able to return the total message count."""
        mock_api.get(
            f"{BASE_URL}/messages?page=1",
            status_code=200,
            json=auth_response_callback(
                mocks.token, mocks.json_messages_page_1, status_code=200
            ),
        )
        count = self.get_controller(mocks.token).get_count()
        assert count == 4

    def test_should_offer_an_iterator_over_messages(
        self, mock_api, mocks, auth_response_callback
    ):
        """A message controller should offer an iterator over messages."""
        mock_api.get(
            f"{BASE_URL}/messages?page=1",
            status_code=200,
            json=auth_response_callback(
                mocks.token, mocks.json_messages_page_1, status_code=200
            ),
        )
        mock_api.get(
            f"{BASE_URL}/messages?page=2",
            status_code=200,
            json=auth_response_callback(
                mocks.token, mocks.json_messages_page_2, status_code=200
            ),
        )
        messages = list(self.get_controller(mocks.token).message_intros)
        assert len(messages) == 4
        assert messages[0] == mocks.message_intro

    def test_should_be_able_to_return_the_full_message_info(
        self, mock_api, mocks, auth_response_callback
    ):
        """A message controller should be able to return the full message info."""
        mock_api.get(
            f"{BASE_URL}/messages/{mocks.message_intro.id}",
            status_code=200,
            json=auth_response_callback(
                mocks.token, mocks.json_message_info, status_code=200
            ),
        )
        message = self.get_controller(mocks.token).get_message(mocks.message_intro.id)
        assert message == mocks.message_info
