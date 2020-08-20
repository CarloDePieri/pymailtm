import signal
import sys
from pymailtm.pymailtm import MailTm, Account, Message


def init():
    def signal_handler(sig, frame):
        print('\n\nClosing! Bye!')
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    MailTm().monitor_new_account()
