from pydantic import BaseModel

from pymailtm.api.credentials import Credentials


class Token(BaseModel):
    token: str


class AuthController:

    endpoint = "token"

    def __init__(self, connection_manager):
        self.connection_manager = connection_manager

    def authenticate(self, credentials: Credentials) -> Token:
        response = self.connection_manager.post(self.endpoint, credentials.model_dump())
        return Token(**response.json())
