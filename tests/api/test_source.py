from pymailtm.api.connection_manager import ConnectionManager
from pymailtm.api.source import SourceController
from conftest import BASE_URL


class TestASourceController:
    """Test: A Source Controller..."""

    def test_should_be_able_to_download_a_message_source(
        self, mock_api, mocks, auth_response_callback
    ):
        """A source controller should be able to download a message source."""
        mock_api.get(
            f"{BASE_URL}/sources/{mocks.message_intro.id}",
            status_code=200,
            json=auth_response_callback(
                mocks.token, mocks.json_message_source, status_code=200
            ),
        )
        connection_manager = ConnectionManager()
        source = SourceController(connection_manager, mocks.token).get_source(
            mocks.message_intro.id
        )
        assert source.data == mocks.message_resource
