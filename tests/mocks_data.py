from dataclasses import dataclass
from typing import List

from pymailtm.api.domain import Domain


@dataclass
class MocksData:
    json_domain = {
        "@id": "/domains/668dc8d8fc74993d22410001",
        "@type": "Domain",
        "createdAt": "2024-07-09T00:00:00+00:00",
        "domain": "dummymailtmdomain.com",
        "id": "668dc8d8fc74993d22410001",
        "isActive": True,
        "isPrivate": False,
        "updatedAt": "2024-07-09T00:00:00+00:00",
    }
    json_domains: dict
    json_domains_pages: List[dict]
    domain: Domain

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
