import json
from enum import Enum
from functools import partial
from typing import Union, Dict, Any

import requests

api_address = "https://api.mail.tm"


class DomainNotAvailableException(Exception):
    """Exception raised when trying to use an unavailable domain in an address."""


class HTTPVerb(Enum):
    """Convenient way to pass an argument to make_api_request."""
    GET = partial(requests.get)
    POST = partial(requests.post)
    DELETE = partial(requests.delete)
    PATCH = partial(requests.patch)


def make_api_request(requests_verb: HTTPVerb,
                     endpoint: str,
                     jwt: Union[str, None] = None,
                     data: Union[Dict[str, Any], None] = None,
                     content: str = "application/json") -> Dict[str, Any]:
    """Send an HTTP request to the webapi endpoint, using the chosen verb.
    If jwt is provided, the request will be authenticated.
    When doing POST or PATCH requests, an optional data argument can be passed to this function.
    It will return the server response."""
    url = f"{api_address}/{endpoint}"
    auth_headers = {
        "accept": "application/ld+json",
        "Content-Type": content
    }

    if jwt:
        auth_headers["Authorization"] = f"Bearer {jwt}"

    if (requests_verb == HTTPVerb.POST or requests_verb == HTTPVerb.PATCH) and data is not None:
        response = requests_verb.value(url, headers=auth_headers, data=json.dumps(data))
    else:
        response = requests_verb.value(url, headers=auth_headers)

    response.raise_for_status()

    if len(response.content) > 0:
        return response.json()
    else:
        # this is the case only for delete
        return {}