from __future__ import annotations
import string
from random import choice

from pydantic import BaseModel
from random_username.generate import generate_username

from pymailtm.api.domain import DomainController
from pymailtm.api.utils import MailTmAPIException


class Credentials(BaseModel):
    """The credentials model used as data in post requests."""

    address: str
    password: str


class CredentialsController:
    """Class used to generate credentials for new accounts."""

    def __init__(self, domain_controller: DomainController):
        self.domain_controller = domain_controller

    def generate(
        self,
        address: str = None,
        password: str = None,
        username: str = None,
    ) -> Credentials:
        """Generate a new set of credentials. If address and password are not provided, they will be generated.
        If username is provided, it will be used to generate the address."""
        if not address:
            address = self.generate_address(username)
        if not password:
            password = self.generate_password(8)
        return Credentials(address=address, password=password)

    def generate_address(self, username: str = None) -> str:
        """Generate a new address. If username is provided, it will be used to generate the address."""
        if not username:
            username = self.generate_username()
        domain = self.domain_controller.get_a_domain()
        if not domain:
            raise MailTmAPIException("No available domain found. Try again later.")
        return f"{username}@{domain.domain}"

    @staticmethod
    def generate_username() -> str:
        """Generate a new username."""
        return generate_username(1)[0].lower()

    @staticmethod
    def generate_password(length: int) -> str:
        """Generate a new random password of given length."""
        letters = string.ascii_letters + string.digits
        return "".join(choice(letters) for _ in range(length))
