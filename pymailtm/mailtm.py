import json
import os
from pathlib import Path
from typing import Optional

import pyperclip

from pymailtm.api.auth import AuthController, Token
from pymailtm.api.credentials import CredentialsController, Credentials
from pymailtm.api.domain import DomainController
from pymailtm.api.connection_manager import (
    ConnectionManager,
    ConnectionManagerWithRateLimiter,
)
from pymailtm.api.account import AccountController, Account
from pymailtm.api.message import MessageController


class Safe:

    db_file = os.path.join(Path.home(), ".pymailtm-test")

    def save_credentials(self, credentials: Credentials) -> None:
        with open(self.db_file, "w+") as db:
            json.dump(credentials.model_dump(), db)

    def load_credentials(self) -> Credentials:
        with open(self.db_file, "r") as db:
            data = json.load(db)
        return Credentials(**data)


class MailTM:

    credentials: Optional[Credentials] = None
    account: Optional[Account] = None
    token: Optional[Token] = None

    message_controller: Optional[MessageController] = None

    def __init__(self, connection_manager: Optional[ConnectionManager] = None):
        self.connection_manager = (
            connection_manager or ConnectionManagerWithRateLimiter()
        )
        self.domain_controller = DomainController(self.connection_manager)
        self.credentials_controller = CredentialsController(self.domain_controller)
        self.account_controller = AccountController(self.connection_manager)
        self.auth_controller = AuthController(self.connection_manager)
        self._safe = Safe()

    def login(self, create_new_account: bool = False) -> Account:
        """Login an account on mail.tm, either by recovering the account from the config file or creating a new one."""
        if create_new_account:
            # create a new set of credentials if needed
            self.credentials = (
                self.credentials or self.credentials_controller.generate()
            )
            # create a new account
            self.account = self.account_controller.create_account(self.credentials)
            # write the credentials to the config file
            self._safe.save_credentials(self.credentials)
            # authenticate the account
            self.token = self.auth_controller.authenticate(self.credentials)
            operation = "created"
        else:
            # recover the credentials from the config file if needed
            self.credentials = self.credentials or self._safe.load_credentials()
            # authenticate the account
            self.token = self.auth_controller.authenticate(self.credentials)
            # get the account details
            self.account = self.account_controller.get_me(self.token)
            operation = "recovered"
        # copy the address to the clipboard
        try:
            pyperclip.copy(self.account.address)
            clipboard = " and copied to the clipboard"
        except pyperclip.PyperclipException:
            clipboard = ""
        # initialize the message controller
        self.message_controller = MessageController(self.connection_manager, self.token)
        print(f"Account {operation}{clipboard}: {self.account.address}")
        return self.account
