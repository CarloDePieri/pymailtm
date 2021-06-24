import json
import os
import random
import re
import shutil
import string
from typing import Type
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

import pytest
import vcr as _vcr
import yagmail
from _pytest.python import Function
from pymailtm import MailTm
from vcr.serialize import deserialize, serialize

default_cassettes_path = "tests/cassettes"

# This option will make vcrpy encrypt all cassettes. Can be turned off to inspect cassette
encrypt_cassettes = True

# Recover from the config file or the env my secrets
secrets_file = ".secrets.json"
if os.path.isfile(secrets_file):
    with open(secrets_file, "r") as f:
        data = json.load(f)
        gmail_mail = data["mail"]
        gmail_password = data["password"]
        encryption_key = data["encryption_key"]
else:
    gmail_mail = os.environ['GMAIL_ADDR']
    gmail_password = os.environ['GMAIL_PASS']
    encryption_key = os.environ['ENCRYPTION_KEY']


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Hook used to make available to fixtures tests results.
    To function this presume no stand-alone test: only tests inside classes are supported."""
    outcome = yield
    rep = outcome.get_result()
    # set a report attribute for each phase of a call, which can
    # be "setup", "call", "teardown"
    setattr(item, "rep_" + rep.when, rep)
    if rep.when == 'setup':
        # This saves all 'setup' report in the class scope as well
        _setup_reports = getattr(item.cls, '_setup_reports', {})
        _setup_reports[(item.nodeid, rep.when)] = rep
        item.cls._setup_reports = _setup_reports


def _mark_cassette_for_deletion(cassette: str, test_class):
    """Insert in a class scoped dictionary the marked cassette. It will be deleted by delete_marked_cassettes."""
    _marked_cassettes = getattr(test_class, '_marked_cassettes', [])
    _marked_cassettes.append(cassette)
    test_class._marked_cassettes = _marked_cassettes


def _mark_test_cassette_for_deletion(node: Function):
    """Mark a test cassette for deletion."""
    test = node.location[2]
    path = node.location[0].replace("tests/", "tests/cassettes/").replace(".py", "")
    cassette = f"{path}/{test}.yaml"
    _mark_cassette_for_deletion(cassette, node.cls)


def _mark_class_setup_cassette_for_deletion(test_class: Type):
    """Mark a class setup cassette for deletion."""
    path = f"{default_cassettes_path}/{test_class.__module__}"
    name = f"{test_class.__name__}_setup"
    cassette = f"{path}/{name}.yaml"
    _mark_cassette_for_deletion(cassette, test_class)


def _has_class_setup_failed(test_class: Type) -> bool:
    """Match the repr in all class setup reports against my class setup style and
    return True if the class setup has failed."""
    for (_, report) in test_class._setup_reports.items():
        pattern = re.compile(r"@pytest\.fixture\(scope=\"class\", autouse=True\)\n\ *def setup\(self")
        found = pattern.search(report.longreprtext)
        if found and report.failed:
            return True
    return False


@pytest.fixture
def vcr_delete_test_cassette_on_failure(request):
    """This fixture will check, at test teardown, if the test has failed: if so, it will delete the test vcr.
    It MUST be used before any other setup fixture, or it won't be able to catch them failing."""
    yield
    if request.node.rep_setup.failed or request.node.rep_call.failed:
        # This particular 'setup' reports consists of function scoped fixtures used by the test
        # For the class scoped setup, use vcr_delete_setup_cassette_on_failure fixture in the setup
        # ---
        # Mark to be deleted the test setup cassette
        # NOTE: leaving this turned off for now. Deleting the setup vcr can invalidate the cache for other tests as well
        # _mark_class_setup_cassette_for_deletion(request.node.cls)
        # Mark to be deleted the actual test cassette
        _mark_test_cassette_for_deletion(request.node)


@pytest.fixture(scope="class")
def vcr_delete_setup_cassette_on_failure(request):
    """This fixture will check, at class teardown, if my class setup has failed: if so, it will delete the setup vcr.
    It must be called as a fixture dependency in the class setup fixture (no usefixtures mark)."""
    yield
    if _has_class_setup_failed(request.cls):
        _mark_class_setup_cassette_for_deletion(request.cls)


@pytest.fixture(scope="class")
def vcr_setup(request):
    """Fixture that allows vcr recording in a class setup.
    It must be called as a fixture dependency in the class setup fixture (no usefixtures mark)."""
    node_id = request.node.nodeid
    el = node_id.split("::")
    path = el[0].replace("tests/", f"{default_cassettes_path}/").replace(".py", "")
    name = f"{el[1]}_setup"
    setup_vcr = _vcr.VCR(record_mode=["once"])
    if encrypt_cassettes:
        setup_vcr.register_persister(EncryptedFilesystemPersister)
    with setup_vcr.use_cassette(f"{path}/{name}.yaml"):
        yield


@pytest.fixture(scope="class", autouse=True)
def delete_marked_cassettes(request):
    """Delete all marked cassettes in the class teardown.
    This is done here because there's a race condition between vcr cassette saving and test teardown, so deleting
    them there is not safe; class teardown, on the other hand, is."""
    yield
    marked_cassettes = getattr(request.cls, '_marked_cassettes', [])
    for cassette in marked_cassettes:
        # Delete both the encrypted and the decrypted cassette
        for path in [cassette, f"{cassette}.enc"]:
            if os.path.exists(path):
                os.remove(path)


# Decorator used as a shortcut for vcr_delete_test_cassette_on_failure fixture
vcr_delete_on_failure = pytest.mark.usefixtures("vcr_delete_test_cassette_on_failure")
# Decorator used to make a test skip VCR recording entirely
vcr_skip = pytest.mark.vcr(before_record_request=lambda _: None)
# Decorator used for consistency
vcr_record = pytest.mark.vcr

# Decorator timeouts: using signal I'm sure that the teardown will be performed
timeout_three = pytest.mark.timeout(3, method='signal')
timeout_five = pytest.mark.timeout(5, method='signal')
timeout_ten = pytest.mark.timeout(10, method='signal')
timeout_fifteen = pytest.mark.timeout(15, method='signal')
timeout_none = pytest.mark.timeout(-1, method='signal')


class EncryptedFilesystemPersister:
    """VCR custom persister that will encrypt and decrypt cassettes with AES-GCM on disk."""

    # NOTE: cryptography encourages the use of Fernet which is a AES-CBC + HMAC but AES-GCM is
    # twice as fast and equally secure as long as nonce are unique

    @classmethod
    def load_cassette(cls, cassette_path, serializer):
        try:
            with open(f"{cassette_path}.enc", "rb") as f:
                nonce, tagged_ciphertext = [f.read(x) for x in (12, -1)]
        except OSError:
            raise ValueError("Cassette not found.")
        # decrypt the cassette with aes-gcm
        cipher = AESGCM(encryption_key.encode())
        # no Authenticated Associated Data (aad) was used, hence None
        cassette_content = cipher.decrypt(nonce, tagged_ciphertext, None)
        # Deserialize it
        cassette = deserialize(cassette_content, serializer)
        return cassette

    @staticmethod
    def save_cassette(cassette_path, cassette_dict, serializer):
        data = serialize(cassette_dict, serializer)
        dirname, _ = os.path.split(cassette_path)
        if dirname and not os.path.exists(dirname):
            os.makedirs(dirname)
        # encrypt the cassette with aes-gcm
        cipher = AESGCM(encryption_key.encode())
        # make sure the nonce is unique every time
        nonce = os.urandom(12)
        # no Authenticated Associated Data (aad) is needed; cryptography implementation
        # will bundle the tag together with the ciphertext
        tagged_ciphertext = cipher.encrypt(nonce, data.encode(), None)
        # save to the file both the nonce and the budled tag and ciphertext
        with open(f"{cassette_path}.enc", "wb") as f:
            [f.write(x) for x in (nonce, tagged_ciphertext)]


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
# Configuration hook for pytest-recording: in here the vcr object can be accessed
#
def pytest_recording_configure(config, vcr):
    if encrypt_cassettes:
        vcr.register_persister(EncryptedFilesystemPersister)


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
    yag = yagmail.SMTP(gmail_mail, gmail_password)
    yag.send(to, 'subject', 'test')
