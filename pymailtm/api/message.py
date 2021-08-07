from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Union, List

import pymailtm.api as api
from pymailtm.api.utils import make_api_request, HTTPVerb


@dataclass
class Message:
    """A message resource from the mail.tm web api."""
    account: api.Account
    id: str
    accountId: str
    msgid: str
    message_from: Dict
    message_to: Dict
    subject: str
    seen: bool
    isDeleted: bool
    hasAttachments: bool
    size: int
    downloadUrl: str
    createdAt: str
    updatedAt: str

    is_full_message: bool = False

    # Fields specific of an intro message
    intro: Union[str, None] = None

    # Fields specific of a full message
    cc: Union[List[Dict[str, str]], None] = None
    bcc: Union[List[Dict[str, str]], None] = None
    flagged: Union[bool, None] = None
    verifications: Union[List, None] = None
    retention: Union[bool, None] = None
    retentionDate: Union[str, None] = None
    text: Union[str, None] = None
    html: Union[List[str], None] = None
    attachments: Union[List[Dict], None] = None

    def __post_init__(self):
        """Method called right after a dataclass __init__"""
        # Set the intro field if coming directly from the full message data
        if self.is_full_message and self.intro is None and self.text is not None:
            text = self.text.replace("\n", " ")[:120]
            if len(self.text) > 120:
                text += "…"
            self.intro = text

    def get_full_message(self) -> None:
        """Download the full message from the web api."""
        data = make_api_request(HTTPVerb.GET,
                                f"messages/{self.id}",
                                self.account.jwt)
        self.is_full_message = True
        self.cc = data["cc"]
        self.bcc = data["bcc"]
        self.flagged = data["flagged"]
        self.verifications = data["verifications"]
        self.retention = data["retention"]
        self.retentionDate = data["retentionDate"]
        self.text = data["text"]
        self.html = data["html"]
        self.attachments = data["attachments"]

    def delete(self) -> bool:
        """Delete the message."""
        make_api_request(HTTPVerb.DELETE, f"messages/{self.id}", self.account.jwt)
        self.account.messages = [message for message in self.account.messages if message.id != self.id]
        self.isDeleted = True
        return self.isDeleted

    def mark_as_seen(self) -> bool:
        """Mark the message as seen."""
        make_api_request(HTTPVerb.PATCH, f"messages/{self.id}", self.account.jwt,
                         data={"seen": True}, content="application/ld+json")
        self.seen = True
        return self.seen

    def get_source(self) -> str:
        """Download the message source."""
        response = make_api_request(HTTPVerb.GET, f"sources/{self.id}", self.account.jwt)
        return response["data"]

    @staticmethod
    def _from_intro_dict(data: Dict, account: api.Account) -> Message:
        """Build a Message object from the dict extracted from the web api response for /messages."""
        return Message(
            account=account,
            id=data["id"],
            accountId=data["accountId"],
            msgid=data["msgid"],
            message_from=data["from"],
            message_to=data["to"],
            subject=data["subject"],
            seen=data["seen"],
            isDeleted=data["isDeleted"],
            hasAttachments=data["hasAttachments"],
            size=data["size"],
            downloadUrl=data["downloadUrl"],
            createdAt=data["createdAt"],
            updatedAt=data["updatedAt"],
            intro=data["intro"]
        )

    @staticmethod
    def _from_full_dict(data: Dict, account: api.Account) -> Message:
        """Build a Message object from the dict extracted from the web api response for /messages/{id}."""
        return Message(
            account=account,
            id=data["id"],
            accountId=data["accountId"],
            msgid=data["msgid"],
            message_from=data["from"],
            message_to=data["to"],
            subject=data["subject"],
            seen=data["seen"],
            isDeleted=data["isDeleted"],
            hasAttachments=data["hasAttachments"],
            size=data["size"],
            downloadUrl=data["downloadUrl"],
            createdAt=data["createdAt"],
            updatedAt=data["updatedAt"],
            is_full_message=True,
            cc=data["cc"],
            bcc=data["bcc"],
            flagged=data["flagged"],
            verifications=data["verifications"],
            retention=data["retention"],
            retentionDate=data["retentionDate"],
            text=data["text"],
            html=data["html"],
            attachments=data["attachments"]
        )