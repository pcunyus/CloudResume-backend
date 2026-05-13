"""
Pytest fixtures for Azure Function counter tests.
"""
import pytest
from unittest.mock import MagicMock, patch
import azure.functions as func


@pytest.fixture
def mock_table_client():
    """Provides a mocked TableClient instance."""
    with patch("function_app.get_table_client") as mock_factory:
        client = MagicMock()
        mock_factory.return_value = client
        yield client


@pytest.fixture
def mock_request_get():
    """Creates a mock GET HttpRequest."""
    req = func.HttpRequest(
        method="GET",
        body=b"",
        url="/api/counter",
    )
    return req


@pytest.fixture
def mock_request_post():
    """Creates a mock POST HttpRequest."""
    req = func.HttpRequest(
        method="POST",
        body=b"",
        url="/api/counter",
    )
    return req
