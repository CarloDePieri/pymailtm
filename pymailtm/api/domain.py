from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List

from pymailtm.api.utils import make_api_request, HTTPVerb


@dataclass
class Domain:
    """A domain resource from the mail.tm web api."""
    id: str
    domain: str
    isActive: bool
    isPrivate: bool
    createdAt: str
    updatedAt: str

    @staticmethod
    def _from_dict(domain_data: Dict) -> Domain:
        """Return a new Domain object starting from a dict of data."""
        return Domain(
            domain_data["id"],
            domain_data["domain"],
            domain_data["isActive"],
            domain_data["isPrivate"],
            domain_data["createdAt"],
            domain_data["updatedAt"]
        )


class DomainManager:
    """Class responsible to get active domains data from the mail.tm web api."""

    @staticmethod
    def get_active_domains() -> List[Domain]:
        """Get from the mail.tm api a list of currently active domains."""
        domains = []
        data = make_api_request(HTTPVerb.GET, "domains")
        for domain_data in data["hydra:member"]:
            domains.append(Domain._from_dict(domain_data))
        return domains

    @staticmethod
    def get_domain(id: str) -> Domain:
        """Get data for the domain corresponding to the given id."""
        data = make_api_request(HTTPVerb.GET, f"domains/{id}")
        return Domain._from_dict(data)


