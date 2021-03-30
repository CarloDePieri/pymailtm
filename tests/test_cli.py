import pytest
import asyncio
import signal
import sys
from time import sleep
from typing import Callable
from unittest.mock import create_autospec

from pymailtm.pymailtm import MailTm
from pymailtm.cli import init


#
# Helpers and fixtures
#
@pytest.fixture
def anyio_backend():
    return 'asyncio'


@pytest.fixture
def backup_sys_argv():
    backup = sys.argv
    yield
    sys.argv = backup


@pytest.fixture
def mocked_login(mocker):
    dummy = create_autospec(MailTm.browser_login)
    return mocker.patch.object(MailTm, "browser_login", new=dummy)


@pytest.fixture
def mocked_monitor(mocker):
    dummy = create_autospec(MailTm.monitor_new_account)
    return mocker.patch.object(MailTm, "monitor_new_account", new=dummy)


#
# Tests
#
@pytest.mark.timeout(15)
class TestTheMailtmScript:
    """The MailTm script..."""

    # This requires an actual graphical environment
    @pytest.mark.graphical
    @pytest.mark.anyio
    async def test_should_close_gracefully_with_ctrl_c(self):
        """... it should close gracefully with ctrl c"""
        # spawn pymailtm in a async subprocess
        proc = await asyncio.create_subprocess_shell("pymailtm")
        # wait for it to spin up
        await asyncio.sleep(1)
        # send a ctrl+c
        proc.send_signal(signal.SIGINT)
        # wait for it to die gracefully
        returncode = await proc.wait()
        # and check the return code
        assert returncode == 0

    def test_should_call_the_right_function_by_default(self, mocked_monitor, backup_sys_argv):
        """... it should call the right function by default"""
        sys.argv = ["pymailtm"]
        init()
        mocked_monitor.assert_called_once()
        call = mocked_monitor.call_args_list[0]
        assert call[1] == {'force_new': False}

    def test_should_monitor_a_new_account_if_required(self, mocked_monitor, backup_sys_argv):
        """... it should monitor a new account if required"""
        sys.argv = ["pymailtm", "-n"]
        init()
        mocked_monitor.assert_called_once()
        call = mocked_monitor.call_args_list[0]
        assert call[1] == {'force_new': True}

    def test_should_launch_the_login_method_with_the_right_argument(self, mocked_login, backup_sys_argv):
        """... it should launch the login method with the right argument"""
        sys.argv = ["pymailtm", "-l"]
        init()
        mocked_login.assert_called_once()
        call = mocked_login.call_args_list[0]
        assert call[1] == {'new': False}

    def test_should_be_able_to_launch_the_login_method_with_a_new_account(self, mocked_login, backup_sys_argv):
        """... it should be able to launch the login method with a new account"""
        sys.argv = ["pymailtm", "-l", "-n"]
        init()
        mocked_login.assert_called_once()
        call = mocked_login.call_args_list[0]
        assert call[1] == {'new': True}
