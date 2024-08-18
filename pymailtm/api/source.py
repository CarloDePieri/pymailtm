from pydantic import BaseModel

from pymailtm.api.connection_manager import ConnectionManager
from pymailtm.api.logger import log
from pymailtm.api.auth import Token
from pymailtm.api.utils import join_path


class Source(BaseModel):
    """The source model."""

    id: str
    data: str
    downloadUrl: str


class SourceController:

    endpoint = "sources"

    def __init__(self, connection_manager: ConnectionManager, token: Token):
        self.connection_manager = connection_manager
        self.token = token

    def get_source(self, message_id: str) -> Source:
        """Get the source of a message.

        NOTE: This leads to the same content as the download_message_source method in the MessageController class.
        """
        log(f"Source requested for message: {message_id}")
        response = self.connection_manager.get(
            join_path(self.endpoint, message_id), token=self.token
        )
        return Source(**response.json())
