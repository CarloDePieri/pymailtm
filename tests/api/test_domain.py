import pytest
from requests import HTTPError

from conftest import BASE_URL
from pymailtm.api.connection_manager import ConnectionManager
from pymailtm.api.domain import DomainController


class TestADomainController:
    """Test: A domain controller..."""

    domain_controller: DomainController

    @pytest.fixture(scope="class", autouse=True)
    def setup(self, request):
        """TestADomainController setup"""
        connection_manager = ConnectionManager(BASE_URL)
        request.cls.domain_controller = DomainController(connection_manager)

    def test_should_be_able_to_recover_available_domains(self, mock_api, mocks):
        """A domain controller should be able to recover available domains."""
        # set up the api mock
        mock_api.get(f"{BASE_URL}/domains", json=mocks.json_domains)
        # request the domains list
        domains = self.domain_controller.get_domains_page()
        assert domains == [mocks.domain]

    def test_should_be_able_to_get_a_domain_info(self, mock_api, mocks):
        """A domain controller should be able to get a domain info."""
        # set up the api mock
        mock_api.get(f"{BASE_URL}/domains/{mocks.domain.id}", json=mocks.json_domain)
        # request the domain info
        domain = self.domain_controller.get_domain(mocks.domain.id)
        assert domain == mocks.domain

    def test_should_raise_a_404_on_non_existing_domain(self, mock_api):
        """A domain controller should raise a 404 on non-existing domain."""
        domain_id = "not-there"
        # set up the api mock
        mock_api.get(f"{BASE_URL}/domains/{domain_id}", status_code=404)
        # request the domain info
        with pytest.raises(HTTPError):
            self.domain_controller.get_domain(domain_id)

    def test_should_offer_an_iterator_over_all_domains(self, mock_api, mocks):
        """A domain controller should offer an iterator over all domains."""
        # set up the api mock
        mock_api.get(f"{BASE_URL}/domains?page=1", json=mocks.json_domains_pages[0])
        mock_api.get(f"{BASE_URL}/domains?page=2", json=mocks.json_domains_pages[1])
        # iterate over the domains
        domains = []
        for domain in self.domain_controller.domains:
            domains.append(domain)
        assert len(domains) == 4
        assert domains[0] == mocks.domain

    def test_iterator_should_work_even_with_only_one_page(self, mock_api, mocks):
        """A domain controller iterator should work even with only one page."""
        # set up the api mock
        mock_api.get(f"{BASE_URL}/domains?page=1", json=mocks.json_domains)
        # iterate over the domains
        domains = list(self.domain_controller.domains)
        assert domains == [mocks.domain]

    def test_should_be_able_to_count_available_domains(self, mock_api, mocks):
        """A domain controller should be able to count available domains."""
        # set up the api mock
        mock_api.get(f"{BASE_URL}/domains", json=mocks.json_domains_pages[0])
        # recover the domains count
        count = self.domain_controller.get_count()
        assert count == 4

    def test_should_have_a_dedicated_method_to_get_a_valid_domain(
        self, mock_api, mocks
    ):
        """A domain controller should have a dedicated method to get a valid domain."""
        # set up the api mock
        mock_api.get(f"{BASE_URL}/domains?page=1", json=mocks.json_domains)
        domain = self.domain_controller.get_a_domain()
        assert domain == mocks.domain
