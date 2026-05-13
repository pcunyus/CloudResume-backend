"""
Unit tests for the visitor counter Azure Function.

Tests mock the CosmosDB TableClient so no live Azure connection is needed.
"""
import json
import sys
import os
from unittest.mock import MagicMock, patch

import pytest
from azure.core.exceptions import ResourceNotFoundError

# Add the api directory to the path so we can import function_app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "api"))

import function_app


class TestGetCount:
    """Tests for the get_count helper function."""

    def test_returns_existing_count(self):
        """Should return the count value from an existing entity."""
        client = MagicMock()
        client.get_entity.return_value = {
            "PartitionKey": "counter",
            "RowKey": "visitors",
            "count": 42,
        }
        result = function_app.get_count(client)
        assert result == 42

    def test_returns_zero_when_no_entity(self):
        """Should return 0 when the entity does not exist yet."""
        client = MagicMock()
        client.get_entity.side_effect = ResourceNotFoundError("Not found")
        result = function_app.get_count(client)
        assert result == 0


class TestIncrementCount:
    """Tests for the increment_count helper function."""

    def test_increments_from_existing_count(self):
        """Should increment an existing count by 1."""
        client = MagicMock()
        client.get_entity.return_value = {
            "PartitionKey": "counter",
            "RowKey": "visitors",
            "count": 10,
        }
        result = function_app.increment_count(client)
        assert result == 11
        client.upsert_entity.assert_called_once()
        upserted = client.upsert_entity.call_args[1]["entity"]
        assert upserted["count"] == 11

    def test_initializes_at_one_when_new(self):
        """Should start at 1 when no entity exists."""
        client = MagicMock()
        client.get_entity.side_effect = ResourceNotFoundError("Not found")
        result = function_app.increment_count(client)
        assert result == 1
        upserted = client.upsert_entity.call_args[1]["entity"]
        assert upserted["count"] == 1


class TestCounterEndpoint:
    """Tests for the HTTP trigger counter function."""

    def test_get_returns_current_count(self, mock_table_client, mock_request_get):
        """GET /api/counter should return current count as JSON."""
        mock_table_client.get_entity.return_value = {
            "PartitionKey": "counter",
            "RowKey": "visitors",
            "count": 5,
        }
        response = function_app.counter(mock_request_get)
        body = json.loads(response.get_body())

        assert response.status_code == 200
        assert body["count"] == 5

    def test_post_increments_and_returns(self, mock_table_client, mock_request_post):
        """POST /api/counter should increment count and return new value."""
        mock_table_client.get_entity.return_value = {
            "PartitionKey": "counter",
            "RowKey": "visitors",
            "count": 99,
        }
        response = function_app.counter(mock_request_post)
        body = json.loads(response.get_body())

        assert response.status_code == 200
        assert body["count"] == 100

    def test_response_is_json_content_type(self, mock_table_client, mock_request_get):
        """Response Content-Type should be application/json."""
        mock_table_client.get_entity.return_value = {
            "PartitionKey": "counter",
            "RowKey": "visitors",
            "count": 1,
        }
        response = function_app.counter(mock_request_get)
        assert response.mimetype == "application/json"

    def test_handles_database_error_gracefully(self, mock_table_client, mock_request_get):
        """Should return 500 with error message on database failure."""
        mock_table_client.get_entity.side_effect = Exception("Connection failed")
        response = function_app.counter(mock_request_get)
        body = json.loads(response.get_body())

        assert response.status_code == 500
        assert "error" in body
