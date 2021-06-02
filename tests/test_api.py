import pytest
import re

from typing import List

from random_username.generate import generate_username
from pymailtm.api import Account, AccountManager, Domain, DomainManager, DomainNotAvailableException


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


@pytest.mark.vcr
class TestADomainManager:
    """Test: A DomainManager..."""

    domains: List[Domain]

    @pytest.fixture(scope="class", autouse=True)
    def setup(self, request):
        request.cls.domains = DomainManager.getActiveDomains()

    def test_should_be_able_to_return_active_domains(self):
        """It should be able to return active domains"""
        assert len(self.domains) > 0
        assert isinstance(self.domains[0], Domain)

    def test_should_be_able_to_get_an_existing_domain_data(self):
        """It should be able to get an existing domain data"""
        domain = self.domains[0]
        domain_data = DomainManager.getDomain(domain.id)
        assert domain.domain == domain_data.domain


class TestAnAccount:
    """Test: An Account..."""

    def test_should_save_all_required_fields(self):
        """It should save all required fields"""
        id_ = "000011"
        address = "account@testdomain.com"
        quota = 40000
        used = 0
        isDisabled = True
        isDeleted = False
        createdAt = "2021-05-22T00:00:00+00:00"
        updatedAt = "2021-05-22T00:00:00+00:00"
        password = "secure"

        test_account = Account(id_, address, quota, used, isDisabled, isDeleted, createdAt, updatedAt, password)

        assert test_account.id == id_
        assert test_account.address == address
        assert test_account.quota == quota
        assert test_account.used == used
        assert test_account.isDisabled == isDisabled
        assert test_account.isDeleted == isDeleted
        assert test_account.createdAt == createdAt
        assert test_account.updatedAt == updatedAt
        assert test_account.password == password


class TestAnAccountManager:
    """Test: An AccountManager..."""

    def test_should_be_able_to_generate_a_valid_address_with_no_arguments(self):
        """It should be able to generate a valid address with no arguments"""
        address = AccountManager.generate_address()
        reg = r"[^@]+@[^@]+\.[^@]+"
        assert re.fullmatch(reg, address) is not None

    def test_should_be_able_to_generate_a_valid_address_with_the_provided_arguments(self):
        """It should be able to generate a valid address with the provided arguments"""
        valid_domain = DomainManager.getActiveDomains()[0]
        address = AccountManager.generate_address(user="nick", domain=valid_domain.domain)
        assert address == f"nick@{valid_domain.domain}"

    def test_should_raise_an_error_with_an_invalid_domain(self):
        """It should raise an error with an invalid domain"""
        with pytest.raises(DomainNotAvailableException):
            AccountManager.generate_address(user="nick", domain="invalid.nope")

    def test_should_be_able_to_generate_a_random_password(self):
        """It should be able to generate a random password"""
        password = AccountManager._generate_password(6)
        assert len(password) == 6
        assert type(password) is str

    def test_should_be_able_to_create_an_account_from_a_dict(self):
        """It should be able to create an Account from a dict"""
        data = {"id": "000011",
                "address": "account@testdomain.com",
                "quota": 40000,
                "used": 0,
                "isDisabled": True,
                "isDeleted": False,
                "createdAt": "2021-05-22T00:00:00+00:00",
                "updatedAt": "2021-05-22T00:00:00+00:00",
                "password": "secure"
                }
        account = AccountManager._account_from_dict(data)
        assert isinstance(account, Account)
        assert account.id == data["id"]

    def test_should_be_able_to_create_an_account_with_no_arguments(self):
        """It should be able to create an account with no arguments"""
        account = AccountManager.new()
        assert isinstance(account, Account)
        assert len(account.address) > 0
        assert len(account.password) == 6

    def test_should_be_able_to_create_an_account_with_the_specified_arguments(self):
        """It should be able to create an account with the specified arguments"""
        user = generate_username(1)[0].lower()
        domain = DomainManager.getActiveDomains()[0].domain
        password = "secure"
        account = AccountManager.new(user=user, domain=domain, password=password)
        assert isinstance(account, Account)
        assert account.address == f"{user}@{domain}"
        assert account.password == password
