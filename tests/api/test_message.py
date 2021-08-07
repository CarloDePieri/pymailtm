from typing import Dict, Any

import pytest

from tests.api.helpers import ensure_at_least_a_message
from tests.conftest import vcr_record, vcr_delete_on_failure, timeout_five

from pymailtm.api import Account, AccountManager, Message


@vcr_record
@vcr_delete_on_failure
@timeout_five
class TestAMessage:
    """Test: A Message..."""

    data: Dict[str, Any]
    data_full: Dict[str, Any]
    account: Account

    @pytest.fixture(scope="class", autouse=True)
    def setup(self, request, vcr_setup, vcr_delete_setup_cassette_on_failure):
        request.cls.account = AccountManager.new()
        request.cls.data = {
            "id": "60bfa3ebf944810cc4987a6a",
            "accountId": "/accounts/60bdfa42aa8bf07f8c2cf886",
            "msgid": "<CADwTKWmdEaO3iBTZwSuVHgBnXt5Aqyc0OHOLVQvwQZpcwF11tg@mail.dummy.com>",
            "from": {
                "address": "sender@dummy.com",
                "name": "nick"
            },
            "to": [
                {
                    "address": "test@logicstreak.com",
                    "name": ""
                }
            ],
            "subject": "Fwd: test",
            "intro": "---------- Forwarded message --------- Da: nick <sender@dummy.com> Date: mar 8 giu 2021 alle ore 19:05 Subject: test To:…",
            "seen": False,
            "isDeleted": False,
            "hasAttachments": False,
            "size": 3566,
            "downloadUrl": "/messages/60bfa3ebf944810cc4987a6a/download",
            "createdAt": "2021-06-08T17:07:07+00:00",
            "updatedAt": "2021-06-08T17:07:55+00:00"
        }
        request.cls.data_full = {
            "id": "60bfa3ebf944810cc4987a6a",
            "accountId": "/accounts/60bdfa42aa8bf07f8c2cf886",
            "msgid": "<CADwTKWmdEaO3iBTZwSuVHgBnXt5Aqyc0OHOLVQvwQZpcwF11tg@mail.dummy.com>",
            "from": {
                "address": "sender@dummy.com",
                "name": "nick"
            },
            "to": [
                {
                    "address": "test@logicstreak.com",
                    "name": ""
                }
            ],
            "cc": [
                {
                    "address": "test2@logicstreak.com",
                    "name": ""
                }
            ],
            "bcc": [],
            "subject": "Fwd: test",
            "seen": False,
            "flagged": False,
            "isDeleted": False,
            "verifications": [],
            "retention": True,
            "retentionDate": "2021-06-15T17:07:55+00:00",
            "text": "---------- Forwarded message ---------\nDa: nick <sender@dummy.com>\nDate: mar 8 giu 2021 alle ore 19:05\nSubject: test\nTo: <test@logisticstreak.com>\n\n\nbanana",
            "html": [
                "<div dir=\"ltr\"><br><br><div class=\"gmail_quote\"><div dir=\"ltr\" class=\"gmail_attr\">---------- Forwarded message ---------<br>Da: <strong class=\"gmail_sendername\" dir=\"auto\">Nick</strong> <span dir=\"auto\">&lt;<a href=\"mailto:sender@dummy.com\">sender@dummy.com</a>&gt;</span><br>Date: mar 8 giu 2021 alle ore 19:05<br>Subject: test<br>To:  &lt;<a href=\"mailto:test@logisticstreak.com\">test@logisticstreak.com</a>&gt;<br></div><br><br><div dir=\"ltr\">banana</div>\r\n</div></div>"
            ],
            "hasAttachments": False,
            "attachments": [
                {
                    "id": "ATTACH000001",
                    "filename": "test_file.txt",
                    "contentType": "text/plain",
                    "disposition": "attachment",
                    "transferEncoding": "base64",
                    "related": False,
                    "size": 1,
                    "downloadUrl": "/messages/60c20b14c139b1f5df8481fa/attachment/ATTACH000001"
                }
            ],
            "size": 3566,
            "downloadUrl": "/messages/60bfa3ebf944810cc4987a6a/download",
            "createdAt": "2021-06-08T17:07:07+00:00",
            "updatedAt": "2021-06-08T17:07:55+00:00"
        }

    def test_should_have_all_required_fields(self):
        """It should have all required fields"""
        data = self.data
        message = Message(
            self.account,
            data["id"],
            data["accountId"],
            data["msgid"],
            data["from"],
            data["to"],
            data["subject"],
            data["seen"],
            data["isDeleted"],
            data["hasAttachments"],
            data["size"],
            data["downloadUrl"],
            data["createdAt"],
            data["updatedAt"],
            intro=data["intro"]
        )
        assert message.account is self.account
        assert message.id == data["id"]
        assert message.accountId == data["accountId"]
        assert message.msgid == data["msgid"]
        assert message.message_from == data["from"]
        assert message.message_to == data["to"]
        assert message.subject == data["subject"]
        assert message.seen == data["seen"]
        assert message.isDeleted == data["isDeleted"]
        assert message.hasAttachments == data["hasAttachments"]
        assert message.size == data["size"]
        assert message.downloadUrl == data["downloadUrl"]
        assert message.createdAt == data["createdAt"]
        assert message.updatedAt == data["updatedAt"]
        assert message.intro == data["intro"]
        assert not message.is_full_message

        data_full = self.data_full
        full_message = Message(
            self.account,
            data_full["id"],
            data_full["accountId"],
            data_full["msgid"],
            data_full["from"],
            data_full["to"],
            data_full["subject"],
            data_full["seen"],
            data_full["isDeleted"],
            data_full["hasAttachments"],
            data_full["size"],
            data_full["downloadUrl"],
            data_full["createdAt"],
            data_full["updatedAt"],
            is_full_message=True,
            cc=data_full["cc"],
            bcc=data_full["bcc"],
            flagged=data_full["flagged"],
            verifications=data_full["verifications"],
            retention=data_full["retention"],
            retentionDate=data_full["retentionDate"],
            text=data_full["text"],
            html=data_full["html"],
            attachments=data_full["attachments"]
        )
        assert full_message.is_full_message
        assert full_message.intro == data["intro"]
        assert full_message.cc == data_full["cc"]
        assert full_message.bcc == data_full["bcc"]
        assert full_message.flagged == data_full["flagged"]
        assert full_message.verifications == data_full["verifications"]
        assert full_message.retention == data_full["retention"]
        assert full_message.retentionDate == data_full["retentionDate"]
        assert full_message.text == data_full["text"]
        assert full_message.html == data_full["html"]
        assert full_message.attachments == data_full["attachments"]

    def test_should_be_able_to_build_a_message_from_a_intro_message_dict(self):
        """It should be able to build a Message from a intro message dict"""
        message = Message._from_intro_dict(self.data, self.account)
        assert isinstance(message, Message)
        assert message.account is self.account
        assert message.id == self.data["id"]
        assert message.intro == self.data["intro"]
        assert not message.is_full_message

    def test_should_be_able_to_build_a_message_from_a_full_message_dict(self):
        """It should be able to build a Message from a full message dict"""
        message = Message._from_full_dict(self.data_full, self.account)
        assert isinstance(message, Message)
        assert message.account is self.account
        assert message.id == self.data_full["id"]
        assert message.text == self.data_full["text"]
        assert message.is_full_message

    def test_should_have_a_method_to_download_the_full_message_data(self):
        """It should have a method to download the full message data"""
        account = self.account
        ensure_at_least_a_message(account)
        message = account.messages[0]
        message.get_full_message()
        assert message.is_full_message
        assert message.text is not None

    def test_should_be_possible_to_delete_a_message(self):
        """It should be possible to delete a message"""
        account = self.account
        ensure_at_least_a_message(account)
        message = account.messages[0]
        messages_before = len(account.messages)
        deleted = message.delete()
        assert deleted
        assert message.isDeleted
        # Ensure that the message has been deleted locally
        assert len(account.messages) == messages_before - 1
        # Ensure the message has been deleted on the server as well
        account.get_all_messages_intro()
        assert len(account.messages) == messages_before - 1

    def test_should_be_markable_as_seen(self):
        """It should be markable as seen"""
        account = self.account
        ensure_at_least_a_message(account)
        message = account.messages[0]
        seen = message.mark_as_seen()
        assert seen
        assert message.seen
        # To make sure the message has been marked on the server clear the list and redownload it
        account.messages = []
        account.get_all_messages_intro()
        seen_message = list(filter(lambda m: m.id == message.id, account.messages))[0]
        assert seen_message.seen

    def test_should_be_possible_to_download_the_source(self):
        """It should be possible to download the source"""
        account = self.account
        ensure_at_least_a_message(account)
        message = account.messages[0]
        source = message.get_source()
        assert len(source) > 0
        assert source.find("Delivered-To:") == 0