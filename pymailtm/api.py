import requests

from dataclasses import dataclass
from typing import Dict, List


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
        """TODO"""
        r = requests.get(f"{api_address}/domains/{id}")
        response = r.json()
        return DomainManager._domain_from_dict(response)

    @staticmethod
    def _domain_from_dict(domain_data: Dict):
        """Return a new Domain object starting from a dict of data."""
        return Domain(
            domain_data["id"],
            domain_data["domain"],
            domain_data["isActive"],
            domain_data["isPrivate"],
            domain_data["createdAt"],
            domain_data["updatedAt"]
        )
