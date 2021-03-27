import json
import os
import pytest
from pymailtm import MailTm, Account
from pymailtm.pymailtm import generate_username, CouldNotGetAccountException, InvalidDbAccountException, open_webbrowser, Message
from typing import Tuple, Callable, Dict
from pymailtm import MailTm
from unittest.mock import patch, create_autospec, mock_open
import pyperclip
import webbrowser


#
# Helper functions
#
def create_new_account() -> Tuple[str, str, Dict[str, str]]:
    """ use MailTm._make_account_request to create a new random account """
    mt = MailTm()
    domain = mt._get_domains_list()[0]
    username =  generate_username(1)[0].lower()
    address = f"{username}@{domain}"
    password = mt._generate_password(6)
    response = mt._make_account_request("accounts", address, password)
    return address, password, response


def read_config() -> Dict[str, str]:
    """ read the config file and return the data """
    with open(MailTm.db_file, "r") as db:
        data = json.load(db)
    return data


#
# Tests
#
@pytest.mark.vcr
class TestAMailtmClass:
    """A MailTm class..."""

    def test_has_a_method_to_generate_a_random_password(self):
        """... it has a method to generate a random password"""
        mt = MailTm()
        password1 = mt._generate_password(10)
        password2 = mt._generate_password(10)
        assert type(password1) is str
        assert len(password1) == 10
        assert password1 != password2

    def test_has_a_method_to_get_all_domains_available(self):
        """... it has a method to get all domains available"""
        domains = MailTm()._get_domains_list()
        assert len(domains) > 0
        assert type(domains[0]) is str

    def test_has_a_method_to_register_an_account(self):
        """... it has a method to register an account"""
        _, _, response = create_new_account()
        assert 'id' in response
        assert 'address' in response

    def test_should_raise_an_exception_when_trying_to_register_an_account_incorrectly(self):
        """... it should raise an exception when trying to register an account incorrectly"""
        address, password, _ = create_new_account()
        with pytest.raises(CouldNotGetAccountException):
            # trying to register the same account twice will result in an error from the api
            MailTm._make_account_request("accounts", address, password)

    def test_should_allow_to_recover_the_token_for_an_existing_account(self):
        """... it should allow to recover the token for an existing account"""
        address, password, _ = create_new_account()
        jwt = MailTm._make_account_request("token", address, password)
        assert "token" in jwt
        assert "id" in jwt
        
    def test_should_be_able_to_save_an_account_to_disk(self):
        """... it should be able to save an account to disk"""
        address, password, _ = create_new_account()
        acc = Account('fakeid', address, password)
        MailTm()._save_account(acc)
        data = read_config()
        assert data["id"] == 'fakeid'
        assert data["address"] == address
        assert data["password"] == password

    def test_should_be_able_to_read_an_account_from_disk(self):
        """... it should be able to read an account from disk"""
        address, password, _ = create_new_account()
        acc = Account('fakeid', address, password)
        mt = MailTm()
        mt._save_account(acc)
        loaded_acc = mt._load_account()
        assert acc.password == loaded_acc.password
        assert acc.address == loaded_acc.address

    def test_should_be_able_to_handle_a_broken_config_file(self):
        """... it should be able to handle a broken config file"""
        with open(MailTm.db_file, "w") as f:
            json.dump({}, f)
        with pytest.raises(InvalidDbAccountException):
            MailTm()._load_account()

    def test_should_be_able_to_create_and_save_an_account_without_errors(self):
        """... it should be able to create and save an account without errors"""
        acc = MailTm().get_account()
        jwt = acc.auth_headers["Authorization"][7:]
        assert len(jwt) > 0

    def test_should_be_able_to_create_and_save_an_account_with_a_custom_password(self):
        """... it should be able to create and save an account with a custom password"""
        password = "my_pass"
        acc = MailTm().get_account(password=password)
        assert acc.password == password
        
    def test_has_a_method_to_open_an_account_and_the_browser(self, mocker):
        """... it has a method to open an account and the browser"""
        mt = MailTm()

        _open_account_spy = mocker.spy(mt, "_open_account")
        mocked_open = mocker.patch("pymailtm.pymailtm.webbrowser.open", new=create_autospec(webbrowser.open))

        mt.browser_login()

        _open_account_spy.assert_called()
        mocked_open.assert_called_once_with("https://mail.tm/")

    def test_should_be_able_to_monitor_an_account(self, mocker):
        """... it should be able to monitor an account"""
        mt = MailTm()

        mock_account = mocker.Mock(spec=Account)
        _open_account_spy = mocker.patch.object(mt, "_open_account", return_value=mock_account)

        mt.monitor_new_account()
        
        _open_account_spy.assert_called()
        mock_account.monitor_account.assert_called()
        

@pytest.mark.vcr
class TestAMailtmAccount:
    """A MailTm Account..."""

    def test_should_recover_the_jwt_when_creating_an_object(self):
        """... it should recover the jwt when creating an object"""
        address, password, _ = create_new_account()
        acc = Account('fakeid', address, password)
        jwt = acc.auth_headers["Authorization"][7:]
        assert len(jwt) > 0

    def test_should_raise_an_exception_if_wrong_credentials_are_used(self):
        """... it should raise an exception if wrong credentials are used"""
        with pytest.raises(CouldNotGetAccountException):
            Account('fakeid', "fake_addr", "fake_password")


@pytest.mark.vcr
class TestWhenMailtmOpensAnAccount:
    """When MailTm opens an account..."""

    def test_should_create_a_new_one_with_no_db_file_present(self, mocker):
        """... it should create a new one with no db file present"""
        mt = MailTm()
        if os.path.isfile(mt.db_file):
            os.remove(mt.db_file)

        spied_load = mocker.spy(mt, "_load_account")
        spied_get = mocker.spy(mt, "get_account")
        mocked_copy = mocker.patch("pymailtm.pymailtm.pyperclip.copy", new=create_autospec(pyperclip.copy))

        acc = mt._open_account()

        spied_load.assert_called()
        spied_get.assert_called()
        mocked_copy.assert_called_once_with(acc.address)


    def test_should_be_be_able_to_recover_existing_account(self, mocker):
        """... it should be be able to recover existing account"""
        mt = MailTm()

        account = mt.get_account()

        spied_load = mocker.spy(mt, "_load_account")
        spied_get = mocker.spy(mt, "get_account")
        mocked_copy = mocker.patch("pymailtm.pymailtm.pyperclip.copy", new=create_autospec(pyperclip.copy))

        acc = mt._open_account()

        spied_load.assert_called()
        spied_get.assert_not_called()
        mocked_copy.assert_called_once_with(acc.address)
        assert account.address == acc.address


    def test_should_create_a_new_account_if_required(self, mocker):
        """... it should create a new account if required"""
        mt = MailTm()

        account = mt.get_account()

        spied_load = mocker.spy(mt, "_load_account")
        spied_get = mocker.spy(mt, "get_account")
        mocked_copy = mocker.patch("pymailtm.pymailtm.pyperclip.copy", new=create_autospec(pyperclip.copy))

        acc = mt._open_account(new=True)

        spied_load.assert_not_called()
        spied_get.assert_called()
        mocked_copy.assert_called_once_with(acc.address)
        assert account.address != acc.address


class TestTheOpenWebbrowserUtility():
    """The open webbrowser utility..."""

    def test_should_call_the_webbrowser_library(self, mocker):
        """... it should call the webbrowser library"""
        url = "http://mail.tm"
        mocked_open = mocker.patch("pymailtm.pymailtm.webbrowser.open", new=create_autospec(webbrowser.open))
        open_webbrowser(url)
        mocked_open.assert_called_once_with(url)



class TestAMailMessage():
    """A mail message..."""

    @pytest.mark.runthis
    def test_has_a_method_to_open_itself_in_a_webbrowser(self, mocker):
        """... it has a method to open itself in a webbrowser"""
        mocked_web = mocker.patch("pymailtm.pymailtm.webbrowser.open", new=create_autospec(webbrowser.open))

        m = Message("fake_id", {}, {}, "subject", "intro", "text", "body", {})
        m.open_web()

        mocked_web.assert_called()
