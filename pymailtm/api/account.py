from pydantic import BaseModel

from pymailtm.api.credentials import Credentials
from pymailtm.api.connection_manager import ConnectionManager


class Account(BaseModel):
    id: str
    address: str
    quota: int
    used: int
    isDisabled: bool
    isDeleted: bool
    createdAt: str
    updatedAt: str


class AccountController:

    def __init__(self, connection_manager: ConnectionManager):
        self.connection_manager = connection_manager
        self.endpoint = "accounts"

    def create_account(self, credentials: Credentials) -> Account:
        response = self.connection_manager.post(
            self.endpoint,
            {
                "address": credentials.address,
                "password": credentials.password,
            },
        )
        return Account(**response.json())
