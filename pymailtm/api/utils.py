from typing import Union, Tuple
from urllib.parse import urlencode


def join_path(*segments: Union[str, Tuple[str, ...]]) -> str:
    """Joins URL path segments using '/'. Keeps the first slash if present."""
    joined = "/".join(segment.strip("/") for segment in segments if segment)
    if segments[0].startswith("/"):
        joined = "/" + joined
    return joined


def add_query(url: str, query: dict) -> str:
    """Add query parameters to an url."""
    return f"{url}?{urlencode(query)}"
