import pytest
import re

from typing import List

from random_username.generate import generate_username
from requests.models import HTTPError
from pymailtm.api import Account, AccountManager, Domain, DomainManager, DomainNotAvailableException


# Decorator used to make a test skip VCR recording entirely
skip_vcr = pytest.mark.vcr(before_record_request=lambda x: None)


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


@pytest.mark.vcr
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

    def test_can_login_after_being_created(self):
        """It can login after being created"""
        account = AccountManager.new()
        account.login()
        assert type(account.jwt) is str
        assert len(account.jwt) > 0

    def test_should_have_a_method_to_verify_the_login(self):
        """It should have a method to verify the login"""
        account = AccountManager.new()
        assert not account.is_logged_in()
        account.login()
        assert account.is_logged_in()


@pytest.mark.vcr
class TestAnAccountManager:
    """Test: An AccountManager..."""

    def test_should_be_able_to_generate_a_valid_address_with_no_arguments(self):
        """It should be able to generate a valid address with no arguments"""
        address = AccountManager.generate_address()
        reg = r"[^@]+@[^@]+\.[^@]+"
        assert re.fullmatch(reg, address) is not None

    def test_should_be_able_to_generate_a_valid_address_with_the_provided_arguments(self):
        """It should be able to generate a valid address with the provided arguments"""
        valid_domain = DomainManager.get_active_domains()[0]
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

    @skip_vcr
    def test_should_be_able_to_create_an_account_with_the_specified_arguments(self):
        """It should be able to create an account with the specified arguments"""
        user = generate_username(1)[0].lower()
        domain = DomainManager.get_active_domains()[0].domain
        password = "secure"
        account = AccountManager.new(user=user, domain=domain, password=password)
        assert isinstance(account, Account)
        assert account.address == f"{user}@{domain}"
        assert account.password == password

    def test_should_pass_along_exception_when_creating_users(self):
        """It should pass along exception when creating users"""
        user = generate_username(1)[0].lower()
        AccountManager.new(user=user)
        with pytest.raises(HTTPError):
            AccountManager.new(user=user)

    def test_should_be_able_to_get_a_jwt(self):
        """It should be able to get a JWT"""
        account = AccountManager.new()
        jwt = AccountManager.get_jwt(account.address, account.password)
        assert type(jwt) is str
        assert len(jwt) > 0

    def test_should_raise_an_exception_when_getting_a_jwt_with_wrong_credentials(self):
        """It should raise an exception when getting a JWT with wrong credentials"""
        with pytest.raises(HTTPError):
            AccountManager.get_jwt("nothere@nothere.not", "nope")

    def test_should_be_able_to_login(self):
        """It should be able to login"""
        account = AccountManager.new()
        logged_account = AccountManager.login(account.address, account.password)
        assert isinstance(logged_account, Account)
        assert logged_account.address == account.address
        assert logged_account.password == account.password
        assert logged_account.createdAt == account.createdAt
        assert logged_account.jwt is not None
        assert len(logged_account.jwt) > 0

    def test_should_raise_an_exception_when_loggin_in_with_the_wrong_credentials(self):
        """It should raise an exception when loggin in with the wrong credentials"""
        account = AccountManager.new()
        with pytest.raises(HTTPError) as err:
            AccountManager.login(account.address, "wrong_pass")
        assert '401 Client Error: Unauthorized' in err.value.args[0]
