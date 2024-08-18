from pydantic import BaseModel

from pymailtm.api.logger import log
from pymailtm.api.credentials import Credentials


class Token(BaseModel):
    """The token model."""

    token: str


class AuthController:
    """Class used to authenticate users. It exchanges credentials for a token that can be used for authenticated operations."""

    endpoint = "token"

    def __init__(self, connection_manager):
        self.connection_manager = connection_manager

    def authenticate(self, credentials: Credentials) -> Token:
        """Authenticate a user and return the token."""
        log("Authentication token requested")
        response = self.connection_manager.post(self.endpoint, credentials.model_dump())
        return Token(**response.json())
