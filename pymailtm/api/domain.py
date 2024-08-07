from typing import List, Optional, Iterator

from pydantic import BaseModel

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

    def __init__(self, connection_manager: ConnectionManager):
        self.connection_manager = connection_manager
        self.endpoint = "domains"

    @property
    def domains(self) -> Iterator[Domain]:
        """Return an iterator over the available domains that takes care of pagination."""
        return LinkedCollectionIterator[Domains, Domain](
            self.connection_manager, self.endpoint, Domains
        )

    def get_count(self) -> int:
        """Return the total number of available domains."""
        response = self.connection_manager.get("domains")
        if response.status_code == 200:
            return Domains(**response.json()).hydra_totalItems
        return 0

    def get_page(self, page=1) -> List[Domain]:
        """Return the domains listed in a specific api response page."""
        response = self.connection_manager.get(add_query(self.endpoint, {"page": page}))
        if response.status_code == 200:
            return Domains(**response.json()).hydra_member
        return []

    def get_domain(self, domain_id: str) -> Optional[Domain]:
        """Return a specific domain info."""
        response = self.connection_manager.get(join_path(self.endpoint, domain_id))
        if response.status_code == 200:
            return Domain(**response.json())
        return None
