import json
import os
import pytest
import pyperclip
import threading
import webbrowser
from typing import Tuple, Dict
from time import sleep
from unittest.mock import create_autospec
from queue import Queue

from pymailtm import MailTm, Account
from pymailtm.pymailtm import generate_username, CouldNotGetAccountException, InvalidDbAccountException, open_webbrowser, Message
from tests.conftest import send_test_email, vcr_delete_on_fail


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


# Custom exception used to interrupt loops
class DoneTestingException(Exception):
    """Done testing!"""


#
# Tests
#
@vcr_delete_on_fail
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
        mocked_copy = mocker.patch("pymailtm.pymailtm.pyperclip.copy", new=create_autospec(pyperclip.copy))

        mt.browser_login()

        _open_account_spy.assert_called()
        mocked_open.assert_called_once_with("https://mail.tm/")
        mocked_copy.assert_called_once()

    def test_should_be_able_to_monitor_an_account(self, mocker):
        """... it should be able to monitor an account"""
        mt = MailTm()

        mock_account = mocker.Mock(spec=Account)
        _open_account_spy = mocker.patch.object(mt, "_open_account", return_value=mock_account)

        mt.monitor_new_account()
        
        _open_account_spy.assert_called()
        mock_account.monitor_account.assert_called()


@vcr_delete_on_fail
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

    def test_should_be_able_to_delete_itself(self):
        """... it should be able to delete itself"""
        account = MailTm().get_account()
        account.delete_account()
        with pytest.raises(CouldNotGetAccountException):
            Account(account.id_, account.address, account.password)

    def test_should_return_an_empty_list_with_no_message(self):
        """... it should return an empty list with no message"""
        account = MailTm().get_account()
        messages = account.get_messages()
        assert len(messages) == 0

    @pytest.mark.timeout(15)
    def test_should_return_messages_if_present(self):
        """... it should return messages, if present"""
        account = MailTm().get_account()
        send_test_email(account.address)
        messages = []
        while len(messages) == 0:
            sleep(1)
            messages = account.get_messages()
        message = messages[0]
        assert type(message) is Message
        assert message.subject == "subject"
        assert message.text == "test"

    @pytest.mark.timeout(15)
    def test_should_be_able_to_wait_for_new_messages(self, mocker):
        """... it should be able to wait for new messages"""
        account = MailTm().get_account()

        # Function that will be launched as the monitoring thread
        def monitor(account: Account, queue: Queue) -> None:
            try:
                # Mock the Message.open_web method, since there's no need to actually open the message and
                # the monitor loop will need an exit point
                def open_web(_) -> None:
                    # The message arrived!
                    # Now the monitor loop needs testing to verify that get_messages gets called again.
                    # To do so, replace the Account.get_messages method with the stop_monitor function, that
                    # will raise an exception and let the whole monitoring thread know that it's done.
                    def stop_monitor(_) -> None:
                        raise DoneTestingException()
                    mocker.patch.object(Account, "get_messages", new=stop_monitor)
                mocker.patch.object(Message, "open_web", new=open_web)

                # Start the monitoring
                account.monitor_account()
            except Exception as e:
                # Put the exception in the queue so that the main thread can continue, then exit this thread
                queue.put(e)

        # This queue will be used to lock the main thread on it and wait for the monitoring thread result
        queue = Queue()
        # Create a thread that will launch the monitor_account function on the account
        monitoring_thread = threading.Thread(target=monitor, args=(account, queue))
        # The monitoring thread must be a daemon, because if the test fails that thread must terminate
        monitoring_thread.daemon = True
        # Start the thread and begin monitoring the account
        monitoring_thread.start()

        # send the test mail
        send_test_email(account.address)

        # Block on the queue while waiting for the result
        result = queue.get()

        if type(result) is DoneTestingException:
            # The DoneTestingException was raised, which means that a Message.open_web and then
            # Account.get_messages got called. Everything went as planned!
            assert True
        else:
            # Something is wrong, raise the exception
            raise result


@vcr_delete_on_fail
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

    def test_has_a_method_to_open_itself_in_a_webbrowser(self, mocker):
        """... it has a method to open itself in a webbrowser"""
        mocked_web = mocker.patch("pymailtm.pymailtm.webbrowser.open", new=create_autospec(webbrowser.open))

        m = Message("fake_id", {}, {}, "subject", "intro", "text", "body", {})
        m.open_web()

        mocked_web.assert_called()
