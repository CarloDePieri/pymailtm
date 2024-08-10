from pydantic import BaseModel

from pymailtm.api.auth import Token
from pymailtm.api.utils import join_path
from pymailtm.api.credentials import Credentials
from pymailtm.api.connection_manager import ConnectionManager


class Account(BaseModel):
    """The account model."""

    id: str
    address: str
    quota: int
    used: int
    isDisabled: bool
    isDeleted: bool
    createdAt: str
    updatedAt: str


class AccountController:
    """Class used to interact with the account API."""

    endpoint = "accounts"
    endpoint_me = "me"

    def __init__(self, connection_manager: ConnectionManager):
        self.connection_manager = connection_manager

    def create_account(self, credentials: Credentials) -> Account:
        """Create a new account using the given credentials."""
        response = self.connection_manager.post(
            self.endpoint,
            credentials.model_dump(),
        )
        return Account(**response.json())

    def get_account_by_id(self, account_id: str, token: Token) -> Account:
        """Get an account by its id."""
        response = self.connection_manager.get(
            join_path(self.endpoint, account_id), token=token
        )
        return Account(**response.json())

    def get_me(self, token: Token) -> Account:
        """Get the account associated with the token."""
        response = self.connection_manager.get(self.endpoint_me, token=token)
        return Account(**response.json())

    def delete_account(self, account_id: str, token: Token) -> bool:
        """Delete an account by its id."""
        response = self.connection_manager.delete(
            join_path(self.endpoint, account_id), token=token
        )
        if response.status_code == 204:
            return True
        return False
