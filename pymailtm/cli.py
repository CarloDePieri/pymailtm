#!/usr/bin/env python
from argparse import ArgumentParser
import signal
import sys
from pymailtm import MailTm


def init():
    def signal_handler(sig, frame) -> None:
        print('\n\nClosing! Bye!')
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    parser = ArgumentParser(
        description="A python interface to mail.tm web api. The temp mail address "
                    "will be copied to the clipboard and the utility will then "
                    "wait for a message to arrive. When it does, it will be "
                    "opened in a browser. Exit the loop with ctrl+c.")
    parser.add_argument('-n', '--new-account', action='store_true',
                        help="whether to force the creation of a new account")
    parser.add_argument('-l', '--login', action='store_true',
                        help="print the credentials and open the login page, then exit")
    args = parser.parse_args()

    if args.login:
        MailTm().browser_login(new=args.new_account)
    else:
        MailTm().monitor_new_account(force_new=args.new_account)


if __name__ == "__main__":
    init()
