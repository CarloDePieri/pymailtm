from gc import callbacks
from typing import Callable

import pytest

from pymailtm.api.auth import Token
from pymailtm.api.connection_manager import ConnectionManager
from pymailtm.api.message import MessageController
from conftest import BASE_URL, auth_response_callback


class TestAMessageController:
    """Test: A Message Controller..."""

    get_controller: Callable[[Token], MessageController]

    @pytest.fixture(scope="class", autouse=True)
    def setup(self, request):
        """TestAMessageController setup"""
        request.cls.get_controller = lambda _, token: MessageController(
            ConnectionManager(BASE_URL), token
        )

    def test_should_be_able_to_download_a_message_intros_page(
        self, mock_api, mocks, auth_response_callback
    ):
        """A message controller should be able to download a message intros page."""
        mock_api.get(
            f"{BASE_URL}/messages?page=1",
            status_code=200,
            json=auth_response_callback(
                mocks.token, mocks.json_message_intros_page_1, status_code=200
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
                mocks.token, mocks.json_message_intros_page_1, status_code=200
            ),
        )
        count = self.get_controller(mocks.token).get_count()
        assert count == 4

    def test_should_offer_an_iterator_over_message_intros(
        self, mock_api, mocks, auth_response_callback
    ):
        """A message controller should offer an iterator over message intros."""
        mock_api.get(
            f"{BASE_URL}/messages?page=1",
            status_code=200,
            json=auth_response_callback(
                mocks.token, mocks.json_message_intros_page_1, status_code=200
            ),
        )
        mock_api.get(
            f"{BASE_URL}/messages?page=2",
            status_code=200,
            json=auth_response_callback(
                mocks.token, mocks.json_message_intros_page_2, status_code=200
            ),
        )
        messages = list(self.get_controller(mocks.token).message_intros)
        assert len(messages) == 4
        assert messages[0] == mocks.message_intro

    def test_should_be_able_to_return_the_full_message(
        self, mock_api, mocks, auth_response_callback
    ):
        """A message controller should be able to return the full message."""
        mock_api.get(
            f"{BASE_URL}/messages/{mocks.message_intro.id}",
            status_code=200,
            json=auth_response_callback(
                mocks.token, mocks.json_message, status_code=200
            ),
        )
        message = self.get_controller(mocks.token).get_message(mocks.message_intro.id)
        assert message == mocks.message

    def test_should_offer_an_iterator_for_the_full_messages(
        self, mock_api, mocks, auth_response_callback
    ):
        """A message controller should offer an iterator for the full messages."""
        mock_api.get(
            f"{BASE_URL}/messages?page=1",
            status_code=200,
            json=auth_response_callback(
                mocks.token, mocks.json_message_intros_page_1, status_code=200
            ),
        )
        mock_api.get(
            f"{BASE_URL}/messages?page=2",
            status_code=200,
            json=auth_response_callback(
                mocks.token, mocks.json_message_intros_page_2, status_code=200
            ),
        )
        mock_api.get(
            f"{BASE_URL}/messages/{mocks.message_intro.id}",
            status_code=200,
            json=auth_response_callback(
                mocks.token, mocks.json_message, status_code=200
            ),
        )
        message = list(self.get_controller(mocks.token).messages)
        assert len(message) == 4
        assert message[0] == mocks.message

    def test_should_be_able_to_delete_a_message(
        self, mock_api, mocks, auth_response_callback
    ):
        """A message controller should be able to delete a message."""
        mock_api.delete(
            f"{BASE_URL}/messages/{mocks.message_intro.id}",
            json=auth_response_callback(mocks.token, "", status_code=204),
        )
        result = self.get_controller(mocks.token).delete_message(mocks.message_intro.id)
        assert result

    def test_should_be_able_to_download_a_message_resource(
        self, mock_api, mocks, auth_response_callback
    ):
        """A message controller should be able to download a message resource."""
        mock_api.get(
            f"{BASE_URL}/messages/{mocks.message_intro.id}/download",
            status_code=200,
            text=auth_response_callback(
                mocks.token, mocks.message_resource, status_code=200
            ),
        )
        resource = self.get_controller(mocks.token).download_message_source(
            mocks.message_intro.id
        )
        assert resource == mocks.message_resource
