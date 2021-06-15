from __future__ import annotations

import json
import random
import requests
import string

from random_username.generate import generate_username
from dataclasses import dataclass, field
from typing import Dict, List, Union


api_address = "https://api.mail.tm"


@dataclass
class Domain:
    """A domain resource from the mail.tm web api."""
    id: str
    domain: str
    isActive: bool
    isPrivate: bool
    createdAt: str
    updatedAt: str


@dataclass
class Account:
    """An account resource from the mail.tm web api."""
    id: str
    address: str
    quota: int
    used: 0
    isDisabled: bool
    isDeleted: bool
    createdAt: str
    updatedAt: str
    password: str
    messages: List[Message] = field(default_factory=list)
    jwt: Union[str, None] = None

    def login(self) -> None:
        """Recover a JWT from the api using saved credentials."""
        self.jwt = AccountManager.get_jwt(self.address, self.password)

    def is_logged_in(self) -> bool:
        """Return true if a JWT is available."""
        return type(self.jwt) is str and len(self.jwt) > 0

    def delete(self) -> bool:
        """Delete the Account on the API."""
        auth_headers = {
            "accept": "application/ld+json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.jwt}"
        }
        r = requests.delete(f"{api_address}/accounts/{self.id}", headers=auth_headers)
        r.raise_for_status()
        self.isDeleted = True

    def get_all_messages_intro(self) -> List[Message]:
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
        self.messages = messages
        return messages

    def _download_messages_page(self, page: int) -> List[Message]:
        """Download a page of message intro resources from the web api."""
        messages = []
        auth_headers = {
            "accept": "application/ld+json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.jwt}"
        }
        r = requests.get(f"{api_address}/messages?page={page}", headers=auth_headers)
        r.raise_for_status()
        for message_data in r.json()["hydra:member"]:
            messages.append(Message._from_intro_dict(message_data, self))
        return messages


@dataclass
class Message:
    """A message resource on the web api."""
    account: Account
    id: str
    accountId: str
    msgid: str
    message_from: Dict
    message_to: Dict
    subject: str
    seen: bool
    isDeleted: bool
    hasAttachments: bool
    size: int
    downloadUrl: str
    createdAt: str
    updatedAt: str

    is_full_message: bool = False

    # Fields specific of an intro message
    intro: Union[str, None] = None

    # Fields specific of a full message
    cc: Union[List[Dict[str, str]], None] = None
    bcc: Union[List[Dict[str, str]], None] = None
    flagged: Union[bool, None] = None
    verifications: Union[List, None] = None
    retention: Union[bool, None] = None
    retentionDate: Union[str, None] = None
    text: Union[str, None] = None
    html: Union[List[str], None] = None
    attachments: Union[List[Dict], None] = None

    def __post_init__(self):
        """Method called right after a dataclass __init__"""
        # Set the intro field if coming directly from the full message data
        if self.is_full_message and self.intro is None:
            text = self.text.replace("\n", " ")[:120]
            if len(self.text) > 120:
                text += "…"
            self.intro = text

    def get_full_message(self):
        """Download the full message from the web api."""
        auth_headers = {
            "accept": "application/ld+json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.account.jwt}"
        }
        r = requests.get(f"{api_address}/messages/{self.id}", headers=auth_headers)
        r.raise_for_status()
        data = r.json()
        self.is_full_message = True
        self.cc = data["cc"]
        self.bcc = data["bcc"]
        self.flagged = data["flagged"]
        self.verifications = data["verifications"]
        self.retention = data["retention"]
        self.retentionDate = data["retentionDate"]
        self.text = data["text"]
        self.html = data["html"]
        self.attachments = data["attachments"]

    @staticmethod
    def _from_intro_dict(data: Dict, account: Account) -> Message:
        """Build a Message object from the dict extracted from the web api response for /messages."""
        return Message(
            account=account,
            id=data["id"],
            accountId=data["accountId"],
            msgid=data["msgid"],
            message_from=data["from"],
            message_to=data["to"],
            subject=data["subject"],
            seen=data["seen"],
            isDeleted=data["isDeleted"],
            hasAttachments=data["hasAttachments"],
            size=data["size"],
            downloadUrl=data["downloadUrl"],
            createdAt=data["createdAt"],
            updatedAt=data["updatedAt"],
            intro=data["intro"]
        )

    @staticmethod
    def _from_full_dict(data: Dict, account: Account) -> Message:
        """Build a Message object from the dict extracted from the web api response for /messages/{id}."""
        return Message(
            account=account,
            id=data["id"],
            accountId=data["accountId"],
            msgid=data["msgid"],
            message_from=data["from"],
            message_to=data["to"],
            subject=data["subject"],
            seen=data["seen"],
            isDeleted=data["isDeleted"],
            hasAttachments=data["hasAttachments"],
            size=data["size"],
            downloadUrl=data["downloadUrl"],
            createdAt=data["createdAt"],
            updatedAt=data["updatedAt"],
            is_full_message=True,
            cc=data["cc"],
            bcc=data["bcc"],
            flagged=data["flagged"],
            verifications=data["verifications"],
            retention=data["retention"],
            retentionDate=data["retentionDate"],
            text=data["text"],
            html=data["html"],
            attachments=data["attachments"]
        )


class DomainManager:
    """Class responsible to get active domains data from the mail.tm web api."""

    @staticmethod
    def get_active_domains() -> List[Domain]:
        """Get from the mail.tm api a list of currently active domains."""
        domains = []
        r = requests.get(f"{api_address}/domains")
        response = r.json()
        for domain_data in response["hydra:member"]:
            domains.append(DomainManager._domain_from_dict(domain_data))
        return domains

    @staticmethod
    def get_domain(id: str) -> Domain:
        """Get data for the domain corresponding to the given id."""
        r = requests.get(f"{api_address}/domains/{id}")
        r.raise_for_status()
        response = r.json()
        return DomainManager._domain_from_dict(response)

    @staticmethod
    def _domain_from_dict(domain_data: Dict) -> Domain:
        """Return a new Domain object starting from a dict of data."""
        return Domain(
            domain_data["id"],
            domain_data["domain"],
            domain_data["isActive"],
            domain_data["isPrivate"],
            domain_data["createdAt"],
            domain_data["updatedAt"]
        )


class AccountManager:
    """Class used to create new Account resources and to get logged in Account objects."""

    @staticmethod
    def new(user: Union[str, None] = None,
            domain: Union[str, None] = None,
            password: Union[str, None] = None) -> Account:
        """Create an account on mail.tm."""
        address = AccountManager.generate_address(user, domain)
        if password is None:
            password = AccountManager._generate_password(6)

        account = {"address": address, "password": password}
        data = AccountManager._make_post_request("accounts", account)
        data["password"] = password
        return AccountManager._account_from_dict(data)

    @staticmethod
    def login(address: str, password: str) -> Account:
        """Return an Account object after authorizing it with the web api."""
        jwt = AccountManager.get_jwt(address, password)
        data = AccountManager.get_account_data(jwt)
        data["password"] = password
        return AccountManager._account_from_dict(data, jwt)

    @staticmethod
    def get_account_data(jwt: str, account_id: Union[str, None] = None) -> Dict:
        """Return account data, using a valid JWT. By default target the account that generated the JWT."""
        auth_headers = {
            "accept": "application/ld+json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {jwt}"
        }
        target = "me" if account_id is None else f"accounts/{account_id}"
        r = requests.get(f"{api_address}/{target}", headers=auth_headers)
        r.raise_for_status()
        return r.json()

    @staticmethod
    def _account_from_dict(data: Dict, jwt: Union[str, None] = None) -> Account:
        """Create an Account object starting from a dict."""
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

    @staticmethod
    def generate_address(user: Union[str, None] = None, domain: Union[str, None] = None) -> str:
        """Generate an address.

        Will raise DomainNotAvailableException when trying to use an unavailable domain."""
        valid_domains = DomainManager.get_active_domains()
        if domain is None:
            domain = valid_domains[0].domain
        else:
            if len(list(filter(lambda x: x.domain == domain, valid_domains))) == 0:
                raise DomainNotAvailableException()
        if user is None:
            user = generate_username(1)[0].lower()
        return f"{user}@{domain}"

    @staticmethod
    def get_jwt(address: str, password: str) -> str:
        """Get the JWT associated with the provided address and password."""
        account = {"address": address, "password": password}
        data = AccountManager._make_post_request("token", account)
        return data["token"]

    @staticmethod
    def _make_post_request(endpoint: str, data: Dict) -> Dict:
        """Make a post request to the given endpoint and with the given data."""
        headers = {
            "accept": "application/ld+json",
            "Content-Type": "application/json"
        }
        r = requests.post(f"{api_address}/{endpoint}",
                          data=json.dumps(data), headers=headers)
        r.raise_for_status()
        return r.json()

    @staticmethod
    def _generate_password(length):
        """Generate a random alphanumeric password of the given length."""
        letters = string.ascii_letters + string.digits
        return ''.join(random.choice(letters) for _ in range(length))


class DomainNotAvailableException(Exception):
    """Exception raised when trying to use an unavailable domain in an address."""
