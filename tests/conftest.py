import json
import os
import random
import re
import shutil
import string
from typing import Type

import pytest
import yagmail
from _pytest.nodes import Item
from pymailtm import MailTm

default_cassettes_path = "tests/cassettes"


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Hook used to make available to fixtures tests results."""
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


def _delete_test_cassette(node: Item):
    """Delete a test cassette."""
    test = node.location[2]
    path = node.location[0].replace("tests/", "tests/cassettes/").replace(".py", "")
    cassette = f"{path}/{test}.yaml"
    if os.path.exists(cassette):
        os.remove(cassette)


def _delete_class_setup_cassette(test_class: Type):
    """Delete a class setup cassette."""
    path = f"{default_cassettes_path}/{test_class.__module__}"
    name = f"{test_class.__name__}_setup"
    cassette = f"{path}/{name}.yaml"
    if os.path.exists(cassette):
        os.remove(cassette)


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
        _delete_test_cassette(request.node)


@pytest.fixture(scope="class")
def vcr_delete_setup_cassette_on_failure(request):
    """This fixture will check, at class teardown, if my class setup has failed: if so, it will delete the setup vcr.
    It must be called as a fixture dependency in the class setup fixture (no usefixtures mark)."""
    yield
    if _has_class_setup_failed(request.cls):
        _delete_class_setup_cassette(request.cls)


@pytest.fixture(scope="class")
def vcr_setup(request):
    """Fixture that allows vcr recording in a class setup.
    It must be called as a fixture dependency in the class setup fixture (no usefixtures mark)."""
    import vcr
    node_id = request.node.nodeid
    el = node_id.split("::")
    path = el[0].replace("tests/", f"{default_cassettes_path}/").replace(".py", "")
    name = f"{el[1]}_setup"
    with vcr.use_cassette(f"{path}/{name}.yaml"):
        yield


# Decorator used as a shortcut for vcr_delete_test_cassette_on_failure fixture
vcr_delete_on_failure = pytest.mark.usefixtures("vcr_delete_test_cassette_on_failure")
# Decorator used to make a test skip VCR recording entirely
vcr_skip = pytest.mark.vcr(before_record_request=lambda x: None)


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
