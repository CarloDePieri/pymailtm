import re
from requests.models import HTTPError
from random_username.generate import generate_username

import pytest
from tests.conftest import timeout_five, vcr_delete_on_failure, vcr_record, vcr_skip, send_test_email
from tests.api.helpers import ensure_at_least_a_message

from pymailtm.api import Account, AccountManager, Message, DomainManager
from pymailtm.api.utils import DomainNotAvailableException


@vcr_record
@vcr_delete_on_failure
@timeout_five
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
        account = AccountManager.new(auto_login=False)
        jwt = account.get_jwt()
        assert jwt == account.jwt
        assert type(account.jwt) is str
        assert len(account.jwt) > 0

    def test_should_have_a_method_to_verify_the_login(self):
        """It should have a method to verify the login"""
        account = AccountManager.new(auto_login=False)
        assert not account.is_logged_in()
        account.get_jwt()
        assert account.is_logged_in()

    def test_should_be_possible_to_delete_it(self):
        """It should be possible to delete it"""
        account = AccountManager.new()
        account.delete()
        with pytest.raises(HTTPError) as err:
            AccountManager.login(account.address, account.password)
        # This is a 401 because the login method tries to get a JWT without success
        assert "401 Client Error: Unauthorized" in err.value.args[0]

    def test_should_raise_an_exception_when_trying_to_delete_an_account_without_login(self):
        """It should raise an exception when trying to delete an account without login"""
        account = AccountManager.new(auto_login=False)
        with pytest.raises(HTTPError) as err:
            account.delete()
        assert "401 Client Error: Unauthorized" in err.value.args[0]

    def test_should_be_able_to_download_its_messages_intro(self):
        """It should be able to download its messages intro."""
        account = AccountManager.new()
        # This helper function calls account.get_all_messages_intro()
        ensure_at_least_a_message(account)
        assert isinstance(account.messages[0], Message)
        assert account.messages[0].subject == 'subject'

    def test_should_maintain_a_full_message_cache(self):
        """It should maintain a full message cache"""
        account = AccountManager.new()
        ensure_at_least_a_message(account)
        # Download full message
        assert not account.messages[0].is_full_message
        for message in account.messages:
            message.get_full_message()
        assert account.messages[0].is_full_message
        # Recover messages intro again
        account.get_all_messages_intro()
        # Check that the full message is still there
        assert account.messages[0].is_full_message

    def test_will_raise_an_exception_when_trying_to_download_messages_without_having_logged_in(self):
        """It will raise an exception when trying to download messages without having logged in"""
        account = AccountManager.new(auto_login=False)
        with pytest.raises(HTTPError) as err:
            account.get_all_messages_intro()
        assert "401 Client Error: Unauthorized" in err.value.args[0]

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
        account = Account._from_dict(data)
        assert isinstance(account, Account)
        assert account.id == data["id"]

    def test_can_be_manually_refreshed(self):
        """It can be manually refreshed"""
        account = AccountManager.new()
        before = account.used
        ensure_at_least_a_message(account)
        assert before == account.used
        account.refresh()
        assert before != account.used


@vcr_record
@vcr_delete_on_failure
@timeout_five
class TestAnAccountManager:
    """Test: An AccountManager..."""

    def test_should_be_able_to_generate_a_valid_address_with_no_arguments(self):
        """It should be able to generate a valid address with no arguments"""
        address = AccountManager._generate_address()
        reg = r"[^@]+@[^@]+\.[^@]+"
        assert re.fullmatch(reg, address) is not None

    def test_should_be_able_to_generate_a_valid_address_with_the_provided_arguments(self):
        """It should be able to generate a valid address with the provided arguments"""
        valid_domain = DomainManager.get_active_domains()[0]
        address = AccountManager._generate_address(user="nick", domain=valid_domain.domain)
        assert address == f"nick@{valid_domain.domain}"

    def test_should_raise_an_error_with_an_invalid_domain(self):
        """It should raise an error with an invalid domain"""
        with pytest.raises(DomainNotAvailableException):
            AccountManager._generate_address(user="nick", domain="invalid.nope")

    def test_should_be_able_to_generate_a_random_password(self):
        """It should be able to generate a random password"""
        password = AccountManager._generate_random_password(6)
        assert len(password) == 6
        assert type(password) is str

    def test_should_be_able_to_create_an_account_with_no_arguments(self):
        """It should be able to create an account with no arguments"""
        account = AccountManager.new()
        assert account.is_logged_in()
        assert isinstance(account, Account)
        assert len(account.address) > 0
        assert len(account.password) == 6

    @vcr_skip
    def test_should_be_able_to_create_an_account_with_the_specified_arguments(self):
        """It should be able to create an account with the specified arguments"""
        user = generate_username(1)[0].lower()
        domain = DomainManager.get_active_domains()[0].domain
        password = "secure"
        account = AccountManager.new(user=user, domain=domain, password=password, auto_login=False)
        assert not account.is_logged_in()
        assert isinstance(account, Account)
        assert account.address == f"{user}@{domain}"
        assert account.password == password

    def test_should_pass_along_exception_when_creating_users(self):
        """It should pass along exception when creating users"""
        user = generate_username(1)[0].lower()
        AccountManager.new(user=user, auto_login=False)
        with pytest.raises(HTTPError):
            AccountManager.new(user=user)

    def test_should_be_able_to_get_a_jwt(self):
        """It should be able to get a JWT"""
        account = AccountManager.new(auto_login=False)
        assert account.jwt is None
        jwt = AccountManager.get_jwt(account.address, account.password)
        assert type(jwt) is str
        assert len(jwt) > 0

    def test_should_raise_an_exception_when_getting_a_jwt_with_wrong_credentials(self):
        """It should raise an exception when getting a JWT with wrong credentials"""
        with pytest.raises(HTTPError):
            AccountManager.get_jwt("nothere@nothere.not", "nope")

    def test_should_be_able_to_login(self):
        """It should be able to login"""
        account = AccountManager.new(auto_login=False)
        logged_account = AccountManager.login(account.address, account.password)
        assert isinstance(logged_account, Account)
        assert logged_account.address == account.address
        assert logged_account.password == account.password
        assert logged_account.createdAt == account.createdAt
        assert logged_account.jwt is not None
        assert len(logged_account.jwt) > 0

    def test_should_raise_an_exception_when_loggin_in_with_the_wrong_credentials(self):
        """It should raise an exception when loggin in with the wrong credentials"""
        account = AccountManager.new(auto_login=False)
        with pytest.raises(HTTPError) as err:
            AccountManager.login(account.address, "wrong_pass")
        assert '401 Client Error: Unauthorized' in err.value.args[0]

    def test_can_return_account_data_from_the_id_and_a_jwt(self):
        """It can return account data from the id and a jwt"""
        account = AccountManager.new(auto_login=False)
        jwt = AccountManager.get_jwt(account.address, account.password)
        # This check the request on /me
        account_data = AccountManager.get_account_data(jwt)
        assert account.id == account_data["id"]
        # This check the request on /accounts/{id}
        account_data = AccountManager.get_account_data(jwt, account.id)
        assert account.id == account_data["id"]
