from time import sleep

from api import Account
from conftest import send_test_email


def ensure_at_least_a_message(account: Account) -> None:
    """Check if at least a message is present in the account. If none are found, send a mail and wait for it to arrive
    before returning."""
    starting_messages_length = len(account.get_all_messages_intro())
    if starting_messages_length == 0:
        send_test_email(account.address)
        while len(account.get_all_messages_intro()) == 0:
            # Wait for the mail to arrive
            sleep(1)
        # When failing for the test timeout and combined with vcr the actual messages number could be higher than 1
        assert len(account.messages) > 0