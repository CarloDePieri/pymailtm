import json
import os
import random
import requests
import string
import webbrowser

from random_username.generate import generate_username
from dataclasses import dataclass
from tempfile import NamedTemporaryFile
from time import sleep
from typing import Dict


class MailTm:
    """A python wrapper for mail.tm web api, which is documented here:
       https://api.mail.tm/"""

    api_address = "https://api.mail.tm"

    def _get_domains_list(self):
        r = requests.get("{}/domains".format(self.api_address))
        response = r.json()
        domains = list(map(lambda x: x["domain"], response["hydra:member"]))
        return domains

    def get_account(self, password=None):
        """Create and return a new account."""
        username = (generate_username(1)[0]).lower()
        domain = random.choice(self._get_domains_list())
        address = "{}@{}".format(username, domain)
        if not password:
            password = self._generate_password(6)
        response = self._make_account_request("accounts", address, password)
        return Account(response["id"], response["address"], password)

    def _generate_password(self, length):
        letters = string.ascii_letters + string.digits
        return ''.join(random.choice(letters) for i in range(length))

    @staticmethod
    def _make_account_request(endpoint, address, password):
        account = {"address": address, "password": password}
        headers = {
                "accept": "application/ld+json",
                "Content-Type": "application/json"
                }
        r = requests.post("{}/{}".format(MailTm.api_address, endpoint),
                          data=json.dumps(account), headers=headers)
        return r.json()

    def monitor_new_account(self):
        """Create a new account and monitor it for new messages."""
        account = self.get_account()
        print("New account created: {}".format(account.address))
        account.monitor_account()


class Account:
    """Representing a temprary mailbox."""

    def __init__(self, id, address, password):
        self.id_ = id
        self.address = address
        self.password = password
        # Set the JWT
        jwt = MailTm._make_account_request("authentication_token",
                                           self.address, self.password)
        self.auth_headers = {
                "accept": "application/ld+json",
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(jwt["token"])
                }
        self.api_address = MailTm.api_address

    def get_messages(self, page=1):
        """Download a list of messages currently in the account."""
        r = requests.get("{}/messages?page={}".format(self.api_address, page),
                         headers=self.auth_headers)
        messages = []
        for message_data in r.json()["hydra:member"]:
            message = Message(
                message_data["id"],
                message_data["from"],
                message_data["to"],
                message_data["subject"],
                message_data["intro"],
                message_data,
                )
            r = requests.get(f"{self.api_address}/messages/{message.id_}", headers=self.auth_headers)
            message.text = r.json()["text"]
            message.html = r.json()["html"]
            messages.append(message)
        return messages

    def delete_account(self):
        """Try to delete the account. Returns True if it succeeds."""
        r = requests.delete("{}/accounts/{}".format(self.api_address,
                            self.id_), headers=self.auth_headers)
        return r.status_code == 204

    def monitor_account(self):
        """Keep waiting for new messages and open then in the browser."""
        while True:
            print("\nWaiting for new messages...")
            start = len(self.get_messages())
            while len(self.get_messages()) == start:
                sleep(1)
            print("New message arrived!")
            self.get_messages()[0].open_web()


@dataclass
class Message:
    """Simple data class that holds a message informations."""
    id_: str
    from_: Dict
    to: Dict
    subject: str
    intro: str
    data: Dict

    def open_web(self):
        """Open a temporary html file with the mail inside in the browser."""
        with NamedTemporaryFile(mode="w", delete=False, suffix=".html") as f:

            html = self.html[0].replace("\n", "<br>").replace("\r", "")
            message = """<html>
            <head></head>
            <body>
            <b>from:</b> {}<br>
            <b>to:</b> {}<br>
            <b>subject:</b> {}<br><br>
            {}</body>
            </html>""".format(self.from_, self.to, self.subject, html)

            f.write(message)
            f.flush()
            os.fsync(f)
            file_name = f.name

            # webbrowser must be silent!
            saverr = os.dup(2)
            os.close(2)
            os.open(os.devnull, os.O_RDWR)
            try:
                webbrowser.open("file://{}".format(file_name))
            finally:
                os.dup2(saverr, 2)
                # Wait a second before deleting the tempfile, so that the
                # browser can load it safely
                sleep(1)
                os.remove(file_name)
