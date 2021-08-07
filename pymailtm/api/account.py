from __future__ import annotations
import random
import string
from dataclasses import dataclass, field
from typing import List, Union, cast, Dict, Any

from random_username.generate import generate_username

import pymailtm.api as api
from pymailtm.api.utils import make_api_request, HTTPVerb, DomainNotAvailableException


@dataclass
class Account:
    """An account resource from the mail.tm web api."""
    id: str
    address: str
    quota: int
    used: int
    isDisabled: bool
    isDeleted: bool
    createdAt: str
    updatedAt: str
    password: str
    messages: List[api.Message] = field(default_factory=list)
    jwt: Union[str, None] = None

    def get_jwt(self) -> str:
        """Recover a JWT from the api using saved credentials."""
        self.jwt = AccountManager.get_jwt(self.address, self.password)
        return self.jwt

    def is_logged_in(self) -> bool:
        """Return true if a JWT is available."""
        return type(self.jwt) is str and len(self.jwt) > 0

    def delete(self) -> bool:
        """Delete the Account on the API."""
        make_api_request(HTTPVerb.DELETE,
                         f"accounts/{self.id}",
                         self.jwt)
        self.isDeleted = True
        return self.isDeleted

    def get_all_messages_intro(self) -> List[api.Message]:
        """Download all the account's messages intro from the web api."""
        page = 1
        messages = []
        # Download the first page of messages intro
        page_messages = self._download_messages_page(page)
        while len(page_messages) > 0:
            # Add the page messages to the full list...
            messages += page_messages
            # ... then keep checking the next page until one returns no message
            page += 1
            page_messages = self._download_messages_page(page)
        for message in messages:
            # only add new messages, so to preserve already download full one
            check = list(filter(lambda x: x.id == message.id, self.messages))
            if len(check) == 0:
                self.messages.append(message)
        return self.messages

    def refresh(self) -> None:
        """Download account data and update fields that could have changed."""
        # Type checkers would complain at the following line about the self.jwt type (which
        # could be None) without the cast. That case is handled by the request exception 401,
        # so no need to handle it here.
        data = AccountManager.get_account_data(cast(str, self.jwt), self.id)
        self.used = data["used"]
        self.isDisabled = data["isDisabled"]
        self.updatedAt = data["updatedAt"]

    def _download_messages_page(self, page: int) -> List[api.Message]:
        """Download a page of message intro resources from the web api."""
        messages = []
        data = make_api_request(HTTPVerb.GET,
                                f"messages?page={page}",
                                self.jwt)
        for message_data in data["hydra:member"]:
            messages.append(api.Message._from_intro_dict(message_data, self))
        return messages

    @staticmethod
    def _from_dict(data: Dict[str, Any], jwt: Union[str, None] = None) -> Account:
        """Create an Account object starting from a dict. If given a valid jwt the object
        will represent an already logged in account."""
        return Account(
            id=data["id"],
            address=data["address"],
            quota=data["quota"],
            used=data["used"],
            isDisabled=data["isDisabled"],
            isDeleted=data["isDeleted"],
            createdAt=data["createdAt"],
            updatedAt=data["updatedAt"],
            password=data["password"],
            jwt=jwt
        )


class AccountManager:
    """Class used to create new Account resources and to get logged in Account objects."""

    @staticmethod
    def new(user: Union[str, None] = None,
            domain: Union[str, None] = None,
            password: Union[str, None] = None,
            auto_login: bool = True) -> Account:
        """Create an account on mail.tm."""
        address = AccountManager._generate_address(user, domain)
        if password is None:
            password = AccountManager._generate_random_password(6)

        account = {"address": address, "password": password}
        data = make_api_request(HTTPVerb.POST, "accounts", data=account)
        data["password"] = password
        account = Account._from_dict(data)
        if auto_login:
            account.get_jwt()
        return account

    @staticmethod
    def login(address: str, password: str) -> Account:
        """Return an Account object after authorizing it with the web api."""
        jwt = AccountManager.get_jwt(address, password)
        data = AccountManager.get_account_data(jwt)
        data["password"] = password
        return Account._from_dict(data, jwt)

    @staticmethod
    def get_account_data(jwt: str, account_id: Union[str, None] = None) -> Dict:
        """Return account data, using a valid JWT. By default target the account that generated the JWT."""
        endpoint = "me" if account_id is None else f"accounts/{account_id}"
        return make_api_request(HTTPVerb.GET, endpoint, jwt=jwt)

    @staticmethod
    def get_jwt(address: str, password: str) -> str:
        """Get the JWT associated with the provided address and password."""
        account = {"address": address, "password": password}
        data = make_api_request(HTTPVerb.POST, "token", data=account)
        return data["token"]

    @staticmethod
    def _generate_address(user: Union[str, None] = None, domain: Union[str, None] = None) -> str:
        """Generate an address.

        Will raise DomainNotAvailableException when trying to use an unavailable domain."""
        valid_domains = api.DomainManager.get_active_domains()
        if domain is None:
            domain = valid_domains[0].domain
        else:
            if len(list(filter(lambda x: x.domain == domain, valid_domains))) == 0:
                raise DomainNotAvailableException()
        if user is None:
            user = generate_username(1)[0].lower()
        return f"{user}@{domain}"

    @staticmethod
    def _generate_random_password(length: int) -> str:
        """Generate a random alphanumeric password of the given length."""
        letters = string.ascii_letters + string.digits
        return ''.join(random.choice(letters) for _ in range(length))