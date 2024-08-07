from typing import List, Optional, Iterator

import requests
from pydantic import BaseModel

from pymailtm.api.linked_collection import (
    LinkedCollection,
    LinkedCollectionIterator,
)


class Domain(BaseModel):
    """The domain model."""

    id: str
    domain: str
    isActive: bool
    isPrivate: bool
    createdAt: str
    updatedAt: str


class Domains(LinkedCollection[Domain]):
    """The domains collection model."""


class DomainController:
    """Class used to interact with the domain API."""

    base_url: str

    def __init__(self, base_url: str):
        self.base_url = base_url

    @property
    def domains(self) -> Iterator[Domain]:
        """Return an iterator over the available domains that takes care of pagination."""
        return LinkedCollectionIterator[Domains, Domain](
            self.base_url, "domains", Domains
        )

    def get_count(self) -> int:
        """Return the total number of available domains."""
        response = requests.get(f"{self.base_url}/domains")
        if response.status_code == 200:
            return Domains(**response.json()).hydra_totalItems
        return 0

    def get_page(self, page=1) -> List[Domain]:
        """Return the domains listed in a specific api response page."""
        response = requests.get(f"{self.base_url}/domains?page={page}")
        if response.status_code == 200:
            return Domains(**response.json()).hydra_member
        return []

    def get_domain(self, domain_id: str) -> Optional[Domain]:
        """Return a specific domain info."""
        response = requests.get(f"{self.base_url}/domains/{domain_id}")
        if response.status_code == 200:
            return Domain(**response.json())
        return None
