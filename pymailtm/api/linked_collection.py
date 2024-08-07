import requests
from pydantic import BaseModel, Field
from typing import TypeVar, Generic, List, Callable, Deque


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
        self, base_url: str, endpoint: str, collection_factory: Callable[..., TC]
    ):
        """
        Initialize the iterator.

        Args:
            base_url (str): The base url of the API.
            endpoint (str): The endpoint to call.
            collection_factory (Callable[..., TC]): A callable that returns a LinkedCollection.
        """
        self.factory = collection_factory
        self.base_url = base_url
        self.endpoint = endpoint
        self.current_url = f"{base_url}/{endpoint}?page=1"
        self.elements = Deque[T]()

    def __iter__(self):
        return self

    def __next__(self) -> T:
        if not self.elements:
            if self.current_url:
                # Fetch the next page
                response = requests.get(self.current_url)
                response.raise_for_status()
                # Create the collection and store the elements
                collection = self.factory(**response.json())
                self.elements = Deque[T](collection.hydra_member)

                # Update the current_url for the next iteration
                self.current_url = None
                if collection.hydra_view and collection.hydra_view.hydra_next:
                    self.current_url = (
                        f"{self.base_url}{collection.hydra_view.hydra_next}"
                    )
            else:
                raise StopIteration
        return self.elements.popleft()
