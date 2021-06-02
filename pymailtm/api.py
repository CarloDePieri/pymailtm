import json
import random
import requests
import string

from random_username.generate import generate_username
from dataclasses import dataclass
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


class DomainManager:
    """Class responsible to get active domains data from the mail.tm web api."""

    @staticmethod
    def getActiveDomains() -> List[Domain]:
        """Get from the mail.tm api a list of currently active domains."""
        domains = []
        r = requests.get("{}/domains".format(api_address))
        response = r.json()
        for domain_data in response["hydra:member"]:
            domains.append(DomainManager._domain_from_dict(domain_data))
        return domains

    @staticmethod
    def getDomain(id: str) -> Domain:
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
    """TODO"""

    @staticmethod
    def new(user: Union[str, None] = None,
            domain: Union[str, None] = None,
            password: Union[str, None] = None) -> Account:
        """Create an account on mail.tm."""
        address = AccountManager.generate_address(user, domain)
        if password is None:
            password = AccountManager._generate_password(6)

        account = {"address": address, "password": password}
        headers = {
            "accept": "application/ld+json",
            "Content-Type": "application/json"
        }
        r = requests.post("{}/{}".format(api_address, "accounts"),
                          data=json.dumps(account), headers=headers)
        r.raise_for_status()
        data = r.json()
        data["password"] = password
        return AccountManager._account_from_dict(data)

    @staticmethod
    def _account_from_dict(data: Dict) -> Account:
        return Account(
            id=data["id"],
            address=data["address"],
            quota=data["quota"],
            used=data["used"],
            isDisabled=data["isDisabled"],
            isDeleted=data["isDeleted"],
            createdAt=data["createdAt"],
            updatedAt=data["updatedAt"],
            password=data["password"]
        )

    @staticmethod
    def generate_address(user: Union[str, None] = None, domain: Union[str, None] = None) -> str:
        """Generate an address. 

        Will raise DomainNotAvailableException when trying to use an unavailable domain."""
        valid_domains = DomainManager.getActiveDomains()
        if domain is None:
            domain = valid_domains[0].domain
        else:
            if len(list(filter(lambda x: x.domain == domain, valid_domains))) == 0:
                raise DomainNotAvailableException()
        if user is None:
            user = generate_username(1)[0].lower()
        return f"{user}@{domain}"

    @staticmethod
    def _generate_password(length):
        """Generate a random alphanumeric password of the given length."""
        letters = string.ascii_letters + string.digits
        return ''.join(random.choice(letters) for _ in range(length))


class DomainNotAvailableException(Exception):
    """Exception raised when trying to use an unavailable domain in an address."""
