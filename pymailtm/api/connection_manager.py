from __future__ import annotations
from requests import get, HTTPError, Response
from urllib.parse import urljoin
from time import sleep

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

    def __init__(
        self,
        base_url: str,
        handle_rate_limit: bool = True,
        rate_limit_delay: float = 1,
    ):
        self.base_url = base_url
        self.handle_rate_limit = handle_rate_limit
        self.rate_limit_delay = rate_limit_delay

    @rate_limit_handler
    def get(self, endpoint: str) -> Response:
        """Perform a GET request to the specified endpoint."""
        response = get(urljoin(self.base_url, endpoint))
        raise_for_status(response)
        log(f"HTTP GET {endpoint} -> {response.status_code}: {response.json()}")
        return response
