from __future__ import annotations
from pydantic import BaseModel, Field
from typing import TypeVar, Generic, List, Callable, Deque, TYPE_CHECKING

if TYPE_CHECKING:
    from pymailtm.api.auth import Token
from pymailtm.api.utils import add_query
from pymailtm.api.connection_manager import ConnectionManager


class Mapping(BaseModel):
    # Note: this is in the spec but has no use for now
    variable: str
    property: str
    required: bool


class Search(BaseModel):
    # Note: this is in the spec but has no use for now
    template: str = Field(alias="hydra:template")
    variableRepresentation: str = Field(alias="hydra:variableRepresentation")
    mapping: Mapping = Field(alias="hydra:mapping")


class View(BaseModel):
    """A view model. This is used to navigate through the collection."""

    hydra_first: str = Field(alias="hydra:first")
    hydra_last: str = Field(alias="hydra:last")
    hydra_next: str = Field(None, alias="hydra:next")
    hydra_previous: str = Field(None, alias="hydra:previous")


# Generic type used to indicate the type of the elements in the collection
T = TypeVar("T")


class LinkedCollection(BaseModel, Generic[T]):
    """A generic linked collection model."""

    hydra_member: List[T] = Field(alias="hydra:member")
    hydra_totalItems: int = Field(alias="hydra:totalItems")
    hydra_view: View = Field(None, alias="hydra:view")
    hydra_search: Search = Field(None, alias="hydra:search")


# Generic type used to indicate the type of the collection inheriting from LinkedCollection
TC = TypeVar("TC", bound=LinkedCollection)


class LinkedCollectionIterator(Generic[TC, T]):
    """A generic iterator over a linked collection elements."""

    def __init__(
        self,
        connection_manager: ConnectionManager,
        endpoint: str,
        collection_factory: Callable[..., TC],
        token: Token = None,
    ):
        """
        Initialize the iterator.

        Args:
            connection_manager (ConnectionManager): The connection manager to use.
            endpoint (str): The endpoint to call.
            collection_factory (Callable[..., TC]): A callable that returns a LinkedCollection.
            token (Optional[Token]): The token to use for authentication.
        """
        self.connection_manager = connection_manager
        self.endpoint = endpoint
        self.factory = collection_factory
        self.current_url = add_query(endpoint, {"page": 1})
        self.elements = Deque[T]()
        self.token = token

    def __iter__(self):
        return self

    def __next__(self) -> T:
        if not self.elements and self.current_url:
            # Fetch the next page
            response = self.connection_manager.get(self.current_url, token=self.token)
            # Create the collection and store the elements
            collection = self.factory(**response.json())
            self.elements = Deque[T](collection.hydra_member)

            # Update the current_url for the next iteration
            self.current_url = None
            if collection.hydra_view and collection.hydra_view.hydra_next:
                self.current_url = f"{collection.hydra_view.hydra_next}"

        if not self.elements:
            raise StopIteration

        return self.elements.popleft()
