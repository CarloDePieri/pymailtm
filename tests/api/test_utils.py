from pymailtm.api.utils import join_path, add_query


class TestTheUtilsModule:
    """Test: The Utils module..."""

    def test_should_join_url_segments_handling_slashes(self):
        """The utils module should join url segments handling slashes."""
        assert (
            join_path("https://api.mail.tm", "domains") == "https://api.mail.tm/domains"
        )
        assert join_path("check/", "/domains/") == "check/domains"
        assert join_path("/domains/", "id/") == "/domains/id"
        assert join_path("/test") == "/test"

    def test_should_add_query_parameter_to_an_endpoint(self):
        """The utils module should add query parameter to an endpoint."""
        assert (
            add_query("https://api.mail.tm/domains", {"page": 1})
            == "https://api.mail.tm/domains?page=1"
        )
