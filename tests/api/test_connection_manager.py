import json
import time
from typing import Generator

import pytest
from requests import HTTPError

from pymailtm.api.connection_manager import (
    ConnectionManagerWithRateLimiter,
    ConnectionManager,
)

BASE_URL = "https://api.mail.tm"


class TestAConnectionManager:
    """Test: A Connection Manager..."""

    cm: ConnectionManager

    @pytest.fixture(scope="class", autouse=True)
    def setup(self, request):
        """TestAConnectionManager setup"""
        request.cls.cm = ConnectionManager()

    def test_should_raise_for_http_errors(self, mock_api):
        """A connection manager should raise for http errors."""
        # set up the api mock
        mock_api.get(f"{BASE_URL}/domains", status_code=404)
        # request the endpoint
        with pytest.raises(HTTPError):
            self.cm.get("/domains")

    def test_should_fail_when_hitting_the_rate_limiter(self, mock_api):
        """A connection manager should fail when hitting the rate limiter."""
        # set up the api mock
        mock_api.get(f"{BASE_URL}/domains", status_code=429)
        # request the endpoint
        with pytest.raises(HTTPError):
            self.cm.get("/domains")


class TestACollectionManagerWithRateLimiter:
    """Test: A Collection Manager with rate limiter..."""

    def test_should_handle_rate_limit(self, mock_api, mocks):
        """A connection manager should handle rate limit."""
        cm = ConnectionManagerWithRateLimiter()

        # rate_limiter will always yield true the first time
        # and then check if the elapsed time is less than 1 second (and FAIL THE TEST if it is)
        def rate_limiter() -> Generator[bool, None, None]:
            last_request_time = None
            while True:
                if not last_request_time:
                    last_request_time = time.time()
                    yield True
                else:
                    elapsed_time = time.time() - last_request_time
                    last_request_time = time.time()
                    if elapsed_time < cm.rate_limit_delay:
                        # Another request was made too soon, fail this test
                        raise pytest.fail(
                            "Rate limit not handled by the ConnectionManager"
                        )
                        yield True
                    else:
                        yield False

        rate_limit = rate_limiter()

        def simulate_rate_limit(_, context):
            if next(rate_limit):
                context.status_code = 429
            else:
                context.status_code = 200
                return json.dumps(mocks.json_domains)

        mock_api.register_uri(
            "GET",
            f"{BASE_URL}/domains",
            text=simulate_rate_limit,
        )
        # request the endpoint
        response = cm.get("/domains")
        assert response.json() == mocks.json_domains
