import json
import os
import pytest
import random
import shutil
import string
import yagmail
from pymailtm import MailTm

#
# Default configuration for pytest-recording
#
# record_mode: once - register new cassettes, use existing one but throw an error
#                       if an existing one try to use different web resources
#
@pytest.fixture(scope="module")
def vcr_config():
    return {"record_mode": ["once"]}


#
# Backup the existing config file and restore it after tests are done
#
@pytest.fixture(scope="session")
def backup_config():
    config_file = MailTm.db_file
    letters = string.ascii_letters + string.digits
    seed = ''.join(random.choice(letters) for i in range(6))
    backup_file = os.path.join(os.path.expanduser("~"), f".pymailtm.{seed}.bak")
    if os.path.isfile(config_file):
        shutil.copy(config_file, backup_file)
    yield
    if os.path.isfile(backup_file):
        shutil.copy(backup_file, config_file)
        os.remove(backup_file)


def send_test_email(to: str) -> None:
    """ Send an email using gmail credentials specified in the .gmail.json file """
    with open(".gmail.json", "r") as f:
        data = json.load(f)
    yag = yagmail.SMTP(data["mail"], data["password"])
    yag.send(to, 'subject', 'test')
