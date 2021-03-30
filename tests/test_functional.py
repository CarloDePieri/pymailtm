import asyncio
import json
import os
import pytest
import re
import signal
import yagmail

from typing import Dict
from tests.conftest import send_test_email


#
# Helpers
#
@pytest.fixture(scope='class')
def anyio_backend():
    """Class scoped anyio fixture used in test class setup"""
    return 'asyncio'


async def launch(cmd: str) -> Dict[str, str]:
    """ Async helper function used to launch the script and save its response """
    response = {}

    #  Spawn pymailtm in a async subprocess
    proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE)

    # Read the first line of the output
    out = await proc.stdout.readline()
    regex = r"[\w\.-]+@[\w\.-]+"

    # Recover the used mail
    response["mail"] = re.search(regex, out.decode("UTF-8")).group(0)

    # Send a test mail
    send_test_email(response["mail"])

    # Wait for the mail, then store the resulting output
    response["mail_reaction"] = await proc.stdout.readline()

    # Send ctrl+c to the program
    proc.send_signal(signal.SIGINT)

    # Wait for the process to exit
    response["stdout"], response["stderr"] = await proc.communicate()

    return response

#
# These tests require a graphical environment and a browser to pass. They will fail in a pure console
# environment.
# Also, since they use subprocesses, these cannot take advantage of vcr cassettes and need to make
# real network requests.
#
@pytest.mark.graphical
#
# Since there's serious chance of deadlock if something is wrong in the script, these tests have a 
# timeout. It can be tweaked if too restrictive for the network.
#
@pytest.mark.timeout(15)
class TestWhenUsingPymailtm:
    """When using pymailtm..."""

    config_path = os.path.expanduser("~/.pymailtm")

    cmd: str
    data: Dict[str, str]

    stdout: str
    stderr: str
    mail_reaction: str
    mail: str

    #
    # To make pytest handle correctly the async setup, anyio is used.
    # Since this is an autouse class fixture, a custom anyio_backend fixture must
    # be passed as an argument.
    #
    @pytest.fixture(scope="class", autouse=True, params=["pymailtm", "pymailtm -n"])
    async def setup(self, request, anyio_backend):
        # Save the existing config file
        self._save_config()

        cmd = request.param
        request.cls.cmd = cmd
        request.cls.data = self.data

        # Call the command asynchronously
        response = await launch(cmd)

        # Save response data in the class
        request.cls.mail = response["mail"]
        request.cls.mail_reaction = response["mail_reaction"]
        request.cls.stdout = response["stdout"]
        request.cls.stderr = response["stderr"]
        yield

    def _save_config(self):
        with open(self.config_path, "r") as f:
            self.data = json.load(f)

    # Actual tests

    def test_should_result_in_no_errors(self):
        """... it should result in no errors"""
        self.stderr == ""

    def test_should_open_the_mail_in_the_browser(self):
        """... it should open the mail in the browser"""
        self.mail_reaction == "Opening in existing browser session."

    def test_should_have_created_the_config_file_with_the_mail_in_it(self):
        """... it should have created the config file with the mail in it"""
        with open(self.config_path, "r") as f:
            data = json.load(f)
            assert data.get("address", "") == self.mail

    def test_should_request_a_new_address_with_the_correct_flag(self):
        """... it should request a new address with the correct flag"""
        if self.cmd == "pymailtm -n":
            assert self.data["address"] != self.mail
