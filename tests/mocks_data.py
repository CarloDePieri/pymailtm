import json
from dataclasses import dataclass

from pymailtm.api.message import Attachment, MessageIntro, Message
from pymailtm.api.domain import Domain
from pymailtm.api.account import Account
from pymailtm.api.auth import Token


@dataclass
class MocksData:
    domain: Domain
    account: Account
    token: Token
    attachment = Attachment
    message_intro = MessageIntro
    message = Message

    username = "a8a78e47bc32496aa345b6501aebfda0"
    domain_name = "domain.example"
    domain_id = "668dc8d8fc74993d22410001"
    json_domain = {
        "@id": "/domains/668dc8d8fc74993d22410001",
        "@type": "Domain",
        "createdAt": "2024-07-09T00:00:00+00:00",
        "domain": domain_name,
        "id": domain_id,
        "isActive": True,
        "isPrivate": False,
        "updatedAt": "2024-07-09T00:00:00+00:00",
    }
    json_domains = {
        "@context": "/contexts/Domain",
        "@id": "/domains",
        "@type": "hydra:Collection",
        "hydra:member": [json_domain],
        "hydra:totalItems": 1,
    }
    json_domains_page_1 = {
        "@id": "/domains?page=1",
        "@type": "hydra:PartialCollectionView",
        "hydra:member": [json_domain, json_domain, json_domain],
        "hydra:totalItems": 4,
        "hydra:view": {
            "hydra:first": "/domains?page=1",
            "hydra:last": "/domains?page=2",
            "hydra:next": "/domains?page=2",
        },
    }
    json_domains_page_2 = {
        "@id": "/domains?page=2",
        "@type": "hydra:PartialCollectionView",
        "hydra:member": [json_domain],
        "hydra:totalItems": 4,
        "hydra:view": {
            "hydra:first": "/domains?page=1",
            "hydra:last": "/domains?page=2",
            "hydra:previous": "/domains?page=1",
        },
    }
    json_domains_pages = [json_domains_page_1, json_domains_page_2]
    account_id = "66b66d9cfdf11bf4bf13e676"
    json_new_account = {
        "address": f"{username}@{domain_name}",
        "createdAt": "2024-08-09T19:27:24+00:00",
        "id": account_id,
        "isDeleted": False,
        "isDisabled": False,
        "quota": 40000000,
        "updatedAt": "2024-08-09T19:27:24+00:00",
        "used": 0,
    }
    json_token = {"token": "dummy_token"}
    json_empty_domains = {
        "@context": "/contexts/Domain",
        "@id": "/domains",
        "@type": "hydra:Collection",
        "hydra:member": [],
        "hydra:totalItems": 0,
    }
    message_id = "66b9d17cf26da89c18382e2c"
    json_message_intro = {
        "id": ("%s" % message_id),
        "msgid": "<96ff6d36ae6646cd655be56d6a75f605@yagmail>",
        "from": {"address": f"test_sender@{domain_name}", "name": ""},
        "to": [{"address": f"{username}@{domain_name}", "name": ""}],
        "subject": "subject",
        "intro": "test",
        "seen": False,
        "isDeleted": False,
        "hasAttachments": False,
        "size": 3901,
        "downloadUrl": ("/messages/%s/download" % message_id),
        "sourceUrl": ("/sources/%s" % message_id),
        "createdAt": "2024-08-12T09:10:18+00:00",
        "updatedAt": "2024-08-12T09:10:20+00:00",
        "accountId": f"/accounts/{account_id}",
    }
    json_empty_message_intros = {
        "@id": "/messages",
        "@type": "hydra:Collection",
        "hydra:totalItems": 0,
        "hydra:member": [],
    }
    json_message_intros = {
        "@id": "/messages",
        "@type": "hydra:Collection",
        "hydra:totalItems": 1,
        "hydra:member": [json_message_intro],
    }
    json_message_intros_page_1 = {
        "@id": "/messages?page=1",
        "@type": "hydra:PartialCollectionView",
        "hydra:member": [json_message_intro, json_message_intro, json_message_intro],
        "hydra:totalItems": 4,
        "hydra:view": {
            "hydra:first": "/messages?page=1",
            "hydra:last": "/messages?page=2",
            "hydra:next": "/messages?page=2",
        },
    }
    json_message_intros_page_2 = {
        "@id": "/messages?page=2",
        "@type": "hydra:PartialCollectionView",
        "hydra:member": [json_message_intro],
        "hydra:totalItems": 4,
        "hydra:view": {
            "hydra:first": "/messages?page=1",
            "hydra:last": "/messages?page=2",
            "hydra:previous": "/messages?page=1",
        },
    }
    json_message_intros_pages = [json_message_intros_page_1, json_message_intros_page_2]
    attachment_id = "ATTACH000001"
    json_attachment = {
        "id": ("%s" % attachment_id),
        "filename": "test-image.svg",
        "contentType": "image/svg+xml",
        "disposition": False,
        "transferEncoding": "base64",
        "related": False,
        "size": 1,
        "downloadUrl": ("/messages/%s/attachment/%s" % (message_id, attachment_id)),
    }
    json_message = {
        "@context": "/contexts/Message",
        "@id": ("/messages/%s" % message_id),
        "@type": "Message",
        "id": ("%s" % message_id),
        "msgid": "<96ff6d36ae6646cd655be56d6a75f605@yagmail>",
        "from": {"address": f"test_sender@{domain_name}", "name": ""},
        "to": [{"address": f"{username}@{domain_name}", "name": ""}],
        "cc": [],
        "bcc": [],
        "subject": "subject",
        "intro": "test",
        "seen": False,
        "flagged": False,
        "isDeleted": False,
        "verifications": {
            "tls": {
                "name": "TLS_AES_256_GCM_SHA384",
                "standardName": "TLS_AES_256_GCM_SHA384",
                "version": "TLSv1.3",
            },
            "spf": False,
            "dkim": False,
        },
        "retention": True,
        "retentionDate": "2024-08-19T09:10:20+00:00",
        "text": "test",
        "html": ["<html><head></head><body><div>test</div></body></html>"],
        "hasAttachments": True,
        "attachments": [json_attachment],
        "size": 5414,
        "downloadUrl": ("/messages/%s/download" % message_id),
        "sourceUrl": ("/sources/%s" % message_id),
        "createdAt": "2024-08-12T09:10:18+00:00",
        "updatedAt": "2024-08-12T09:10:20+00:00",
        "accountId": f"/accounts/{account_id}",
    }
    json_me = {
        **json_new_account,
        **{
            "@context": "/contexts/Account",
            "@id": "/me",
            "@type": "Account",
        },
    }
    json_account = {
        **json_me,
        **{"@id": f"/accounts/{account_id}"},
    }
    message_resource = "A full message/rfc822 string.\r\n"
    json_message_source = {
        "id": message_id,
        "downloadUrl": f"/messages/{message_id}/download",
        "data": message_resource,
    }
    test_svg = b'<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n<!-- Created with Inkscape (http://www.inkscape.org/) -->\n\n<svg\n   width="48"\n   height="48"\n   viewBox="0 0 48 48"\n   version="1.1"\n   id="svg1"\n   xmlns="http://www.w3.org/2000/svg"\n   xmlns:svg="http://www.w3.org/2000/svg">\n  <defs\n     id="defs1" />\n  <g\n     id="layer1">\n    <rect\n       style="fill:#ff754e;fill-opacity:1;stroke-width:3.26929;stroke-opacity:0.26"\n       id="rect1"\n       width="48"\n       height="48"\n       x="0"\n       y="0" />\n    <text\n       xml:space="preserve"\n       style="font-style:normal;font-weight:normal;font-size:13.3333px;line-height:1.25;font-family:sans-serif;letter-spacing:0px;word-spacing:0px;fill:#000000;fill-opacity:1;stroke:none"\n       x="12.273367"\n       y="28.326656"\n       id="text1"><tspan\n         id="tspan1"\n         x="12.273367"\n         y="28.326656"\n         style="font-size:13.3333px">test</tspan></text>\n  </g>\n</svg>\n'
    mercure_stream = [
        "id: urn:uuid:bc1b231b-f9ab-4a79-8230-0ffd33995b09",
        "data:" + json.dumps(json_message_intro),
        "\nid: urn:uuid:07b417c1-ab0c-4c97-b4a2-2676e937c3eb",
        "data:" + json.dumps(json_message_intro),
        "\nid: urn:uuid:6baa3b5e-11dc-46c1-800e-882849d56232",
        "data:" + json.dumps(json_message_intro),
    ]
    mercure_stream_messages = "\n".join(mercure_stream)

    def __init__(self):
        self.domain = Domain(**self.json_domain)
        self.account = Account(**self.json_new_account)
        self.token = Token(**self.json_token)
        self.attachment = Attachment(**self.json_attachment)
        self.message_intro = MessageIntro(**self.json_message_intro)
        self.message = Message(**self.json_message)
