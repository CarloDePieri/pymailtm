import json
import os
import pytest
import random
import shutil
import string

import vcr
import yagmail
from dotenv import load_dotenv
from pytest_vcr_delete_on_fail import get_default_cassette_path
from vcrpy_encrypt import BaseEncryptedPersister

from pymailtm import MailTm

load_dotenv(".secrets")


# Define the vcr persister
class MyEncryptedPersister(BaseEncryptedPersister):
    encryption_key: bytes = os.getenv("ENCRYPTION_KEY").encode("utf-8")
    should_output_clear_text_as_well = True


def pytest_recording_configure(config, vcr):
    vcr.register_persister(MyEncryptedPersister)


# Define two helper functions that will take the default path and append vcrpy_encrypt suffixes
def get_encrypted_cassette(item) -> str:
    default = get_default_cassette_path(item)
    return f"{default}{MyEncryptedPersister.encoded_suffix}"


def get_clear_text_cassette(item) -> str:
    default = get_default_cassette_path(item)
    return f"{default}{MyEncryptedPersister.clear_text_suffix}"


# Define a shorthand for the vcr_delete_on_fail marker
vcr_delete_on_fail = pytest.mark.vcr_delete_on_fail([get_encrypted_cassette,
                                                     get_clear_text_cassette])


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
    if os.path.isfile(".gmail.json"):
        with open(".gmail.json", "r") as f:
            data = json.load(f)
            mail = data["mail"]
            password = data["password"]
    else:
        print('env')
        mail = os.environ['GMAIL_ADDR']
        password = os.environ['GMAIL_PASS']
    yag = yagmail.SMTP(mail, password)
    yag.send(to, 'subject', 'test')
