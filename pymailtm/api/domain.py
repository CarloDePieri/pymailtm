from typing import Optional, Iterator

from pydantic import BaseModel

from pymailtm.api.logger import log
from pymailtm.api.utils import join_path, add_query
from pymailtm.api.connection_manager import ConnectionManager
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

    endpoint = "domains"

    def __init__(self, connection_manager: ConnectionManager):
        self.connection_manager = connection_manager

    @property
    def domains(self) -> Iterator[Domain]:
        """Return an iterator over the available domains that takes care of pagination."""
        log("Domains iterator requested")
        return LinkedCollectionIterator[Domains, Domain](
            self.connection_manager, self.endpoint, Domains
        )

    def get_count(self) -> int:
        """Return the total number of available domains."""
        log("Domains count requested")
        return self.get_domains_page().hydra_totalItems

    def get_domains_page(self, page=1) -> Optional[Domains]:
        """Return the domains listed in a specific api response page."""
        log(f"Domains page requested: {page}")
        response = self.connection_manager.get(add_query(self.endpoint, {"page": page}))
        if response.status_code == 200:
            return Domains(**response.json())
        return None

    def get_domain(self, domain_id: str) -> Optional[Domain]:
        """Return a specific domain info."""
        log(f"Domain info requested: {domain_id}")
        response = self.connection_manager.get(join_path(self.endpoint, domain_id))
        if response.status_code == 200:
            return Domain(**response.json())
        return None

    def get_a_domain(self) -> Optional[Domain]:
        """Return a valid domain."""
        log("Domain requested")
        domains = self.get_domains_page()
        if domains.hydra_member:
            return domains.hydra_member[0]
        return None
