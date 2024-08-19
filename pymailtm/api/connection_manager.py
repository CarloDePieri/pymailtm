from __future__ import annotations
from requests import get, post, HTTPError, Response, delete, patch
from urllib.parse import urljoin
from time import sleep
import json

from typing import TYPE_CHECKING, Dict, Optional, Generator

# noinspection PyProtectedMember,PyPackageRequirements
from sseclient import Event, SSEClient

if TYPE_CHECKING:
    from pymailtm.api.auth import Token

from pymailtm.api.logger import log


# Decorator that handles rate limit. Network calls inside the decorated function will be retried, after a delay,
# if the response status code is 429
def rate_limit_handler(func):
    def _decorator(self: ConnectionManager, *args, **kwargs):
        # If the handle_rate_limit attribute is set to True...
        if self.handle_rate_limit:
            while True:
                try:
                    # ... keep trying to execute the method
                    return func(self, *args, **kwargs)
                except HTTPError as e:
                    if e.response.status_code == 429:
                        # If the response status code is 429, wait for 1 second and try again
                        log(f"Rate limit reached: waiting for {self.rate_limit_delay}s")
                        sleep(self.rate_limit_delay)
                    else:
                        # If the response status code is different from 429, raise the exception
                        raise e
        else:
            # If the handle_rate_limit attribute is set to False, just execute the method
            return func(self, *args, **kwargs)

    return _decorator


def raise_for_status(response: Response):
    """If the response status code is not 2xx log it and raise an exception."""
    try:
        response.raise_for_status()
    except HTTPError as e:
        log(f"HTTP error: {e}")
        raise e


class ConnectionManager:
    """Class used to manage and abstract the connection to the API."""

    base_url: str = "https://api.mail.tm"
    mercure_url: str = "https://mercure.mail.tm/.well-known/mercure"

    def __init__(
        self,
        handle_rate_limit: bool = True,
        rate_limit_delay: float = 1,
    ):
        self.handle_rate_limit = handle_rate_limit
        self.rate_limit_delay = rate_limit_delay
        self.headers = {
            "Accept": "application/ld+json",
            "Content-Type": "application/json",
        }

    @rate_limit_handler
    def get(self, endpoint: str, token: Optional[Token] = None) -> Response:
        """Perform a GET request to the specified endpoint. If a token is provided, it will be used for authentication."""
        headers = self._get_authenticated_headers(token)
        response = get(urljoin(self.base_url, endpoint), headers=headers)
        raise_for_status(response)
        self._log("GET", endpoint, response)
        return response

    @rate_limit_handler
    def post(self, endpoint, data: Dict) -> Response:
        """Perform a POST request to the specified endpoint."""
        response = post(
            urljoin(self.base_url, endpoint),
            data=json.dumps(data),
            headers=self.headers,
        )
        raise_for_status(response)
        self._log("POST", endpoint, response)
        return response

    @rate_limit_handler
    def delete(self, endpoint: str, token: Token) -> Response:
        """Perform an authenticated DELETE request to the specified endpoint."""
        headers = self._get_authenticated_headers(token)
        response = delete(urljoin(self.base_url, endpoint), headers=headers)
        raise_for_status(response)
        self._log("DELETE", endpoint, response)
        return response

    @rate_limit_handler
    def patch(self, endpoint: str, data: Dict, token: Token) -> Response:
        """Perform an authenticated PATCH request to the specified endpoint."""
        headers = self._get_authenticated_headers(token)
        headers["Content-Type"] = "application/merge-patch+json"
        response = patch(
            urljoin(self.base_url, endpoint),
            data=json.dumps(data),
            headers=headers,
        )
        raise_for_status(response)
        self._log("PATCH", endpoint, response)
        return response

    def subscribe_for_sse_events(
        self, account_id: str, token: Token
    ) -> Generator[Event, None, None]:
        """Wait for a Mercure update on the '/accounts/{account_id}' topic."""
        params = {"topic": "/accounts/" + account_id}
        headers = self._get_authenticated_headers(token)
        response = get(self.mercure_url, stream=True, params=params, headers=headers)
        raise_for_status(response)
        log(
            f"HTTP STREAM GET with mercure prepared, account id {account_id} -> {response.status_code}"
        )
        # noinspection PyTypeChecker
        # requests.get with stream=True returns a Response that can be used as Generator, the type checker is wrong here
        return SSEClient(event_source=response).events()

    @staticmethod
    def _log(method: str, endpoint: str, response: Response) -> None:
        """Log the request method, endpoint and response status code."""
        if (
            response.headers.get("Content-Type") == "application/json"
            or response.headers.get("Content-Type") == "application/ld+json"
        ):
            data = response.json()
        else:
            data = response.text
        log(f"HTTP {method} {endpoint} -> {response.status_code}: {data}")

    def _get_authenticated_headers(
        self, token: Optional[Token] = None
    ) -> Dict[str, str]:
        """Return the headers with the authentication token if it's provided."""
        headers = self.headers.copy()
        if token:
            headers["Authorization"] = f"Bearer {token.token}"
        return headers
