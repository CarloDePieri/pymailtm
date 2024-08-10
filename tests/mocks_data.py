from dataclasses import dataclass
from typing import List

from pymailtm.api.domain import Domain
from pymailtm.api.account import Account
from pymailtm.api.auth import Token


@dataclass
class MocksData:
    json_domain = {
        "@id": "/domains/668dc8d8fc74993d22410001",
        "@type": "Domain",
        "createdAt": "2024-07-09T00:00:00+00:00",
        "domain": "domain.example",
        "id": "668dc8d8fc74993d22410001",
        "isActive": True,
        "isPrivate": False,
        "updatedAt": "2024-07-09T00:00:00+00:00",
    }
    json_domains: dict
    json_domains_pages: List[dict]
    domain: Domain
    json_new_account = {
        "address": "a8a78e47bc32496aa345b6501aebfda0@domain.example",
        "createdAt": "2024-08-09T19:27:24+00:00",
        "id": "66b66d9cfdf11bf4bf13e676",
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

    def __init__(self):
        self.json_domains = {
            "@context": "/contexts/Domain",
            "@id": "/domains",
            "@type": "hydra:Collection",
            "hydra:member": [self.json_domain],
            "hydra:totalItems": 1,
        }
        domains_page_1 = {
            "@id": "/domains?page=1",
            "@type": "hydra:PartialCollectionView",
            "hydra:member": [self.json_domain, self.json_domain, self.json_domain],
            "hydra:totalItems": 4,
            "hydra:view": {
                "hydra:first": "/domains?page=1",
                "hydra:last": "/domains?page=2",
                "hydra:next": "/domains?page=2",
            },
        }
        domains_page_2 = {
            "@id": "/domains?page=2",
            "@type": "hydra:PartialCollectionView",
            "hydra:member": [self.json_domain],
            "hydra:totalItems": 4,
            "hydra:view": {
                "hydra:first": "/domains?page=1",
                "hydra:last": "/domains?page=2",
                "hydra:previous": "/domains?page=1",
            },
        }
        self.json_domains_pages = [domains_page_1, domains_page_2]
        self.domain = Domain(**self.json_domain)
        self.account = Account(**self.json_new_account)
        self.token = Token(**self.json_token)
        self.json_me = {
            **self.json_new_account,
            **{
                "@context": "/contexts/Account",
                "@id": "/me",
                "@type": "Account",
            },
        }
        self.json_account = {
            **self.json_me,
            **{"@id": "/accounts/66b66d9cfdf11bf4bf13e676"},
        }
