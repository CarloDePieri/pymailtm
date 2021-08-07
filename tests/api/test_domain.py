from typing import List
from requests.models import HTTPError

import pytest
from tests.conftest import vcr_delete_on_failure, vcr_record

from pymailtm.api import Domain, DomainManager


class TestADomain:
    """Test: A Domain..."""

    def test_should_have_all_the_required_fields(self):
        """It should have all the required fields"""
        id_ = "000001"
        domain = "testdomain.com"
        isActive = True
        isPrivate = False
        createdAt = "2021-05-22T00:00:00+00:00"
        updatedAt = "2021-05-22T00:00:00+00:00"

        test_domain = Domain(id_, domain, isActive, isPrivate, createdAt, updatedAt)

        assert test_domain.id == id_
        assert test_domain.domain == domain
        assert test_domain.isActive == isActive
        assert test_domain.isPrivate == isPrivate
        assert test_domain.createdAt == createdAt
        assert test_domain.updatedAt == updatedAt


@vcr_record
@vcr_delete_on_failure
class TestADomainManager:
    """Test: A DomainManager..."""

    domains: List[Domain]

    @pytest.fixture(scope="class", autouse=True)
    def setup(self, request):
        request.cls.domains = DomainManager.get_active_domains()

    def test_should_be_able_to_return_active_domains(self):
        """It should be able to return active domains"""
        assert len(self.domains) > 0
        assert isinstance(self.domains[0], Domain)

    def test_should_be_able_to_get_an_existing_domain_data(self):
        """It should be able to get an existing domain data"""
        domain = self.domains[0]
        domain_data = DomainManager.get_domain(domain.id)
        assert domain.domain == domain_data.domain

    def test_should_raise_an_exception_when_no_domain_with_the_specified_id_is_found(self):
        """It should raise an exception when no domain with the specified id is found"""
        with pytest.raises(HTTPError):
            DomainManager.get_domain("0")
