from typing import List, Optional

from pydantic import BaseModel, Field

from pymailtm.api.auth import Token
from pymailtm.api.linked_collection import LinkedCollection
from pymailtm.api.logger import log
from pymailtm.api.utils import add_query


class Contact(BaseModel):
    """The contact model."""

    address: str
    name: str


class Attachment(BaseModel):
    """The attachment model."""

    id: str
    filename: str
    contentType: str
    disposition: bool
    transferEncoding: str
    related: bool
    size: int
    downloadUrl: str


class Message(BaseModel):
    """The message model."""

    id: str
    msgid: str
    from_: Contact = Field(alias="from")
    to: List[Contact]
    subject: str
    intro: str
    seen: bool
    isDeleted: bool
    hasAttachments: bool
    size: int
    downloadUrl: str
    createdAt: str
    updatedAt: str
    accountId: str


class MessageInfo(Message):
    """The message info model."""

    cc: List[Contact]
    bcc: List[Contact]
    flagged: bool
    verifications: dict
    retention: bool
    retentionDate: str
    text: str
    html: List[str]
    attachments: List[Attachment]
    sourceUrl: str


class Messages(LinkedCollection[Message]):
    """The messages collection model."""


class MessageController:
    """Class used to interact with the message API."""

    endpoint = "messages"

    def __init__(self, connection_manager):
        self.connection_manager = connection_manager

    def get_messages_page(self, token: Token, page=1) -> Optional[Messages]:
        """Return the messages listed in a specific api response page."""
        log(f"Messages page requested: {page}")
        response = self.connection_manager.get(
            add_query(self.endpoint, {"page": page}), token=token
        )
        if response.status_code == 200:
            return Messages(**response.json())
        return None
