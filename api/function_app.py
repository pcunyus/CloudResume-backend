"""
Azure Function — Visitor Counter API
HTTP trigger that reads/increments a visitor count in CosmosDB Table API.
"""
import os
import json
import logging

import azure.functions as func
from azure.data.tables import TableClient
from azure.core.exceptions import ResourceNotFoundError

app = func.FunctionApp()

# Configuration
CONNECTION_STRING = os.getenv("COSMOS_CONNECTION_STRING", "")
TABLE_NAME = os.getenv("COSMOS_TABLE_NAME", "VisitorCounter")
PARTITION_KEY = "counter"
ROW_KEY = "visitors"


def get_table_client() -> TableClient:
    """Create and return a TableClient for the visitor counter table."""
    return TableClient.from_connection_string(
        conn_str=CONNECTION_STRING,
        table_name=TABLE_NAME,
    )


def get_count(table_client: TableClient) -> int:
    """Retrieve the current visitor count from CosmosDB."""
    try:
        entity = table_client.get_entity(
            partition_key=PARTITION_KEY,
            row_key=ROW_KEY,
        )
        return int(entity.get("count", 0))
    except ResourceNotFoundError:
        return 0


def increment_count(table_client: TableClient) -> int:
    """Increment the visitor count and return the new value."""
    current = get_count(table_client)
    new_count = current + 1
    entity = {
        "PartitionKey": PARTITION_KEY,
        "RowKey": ROW_KEY,
        "count": new_count,
    }
    table_client.upsert_entity(entity=entity)
    return new_count


@app.route(route="counter", methods=["GET", "POST"], auth_level=func.AuthLevel.ANONYMOUS)
def counter(req: func.HttpRequest) -> func.HttpResponse:
    """
    GET  /api/counter — Returns current visitor count.
    POST /api/counter — Increments count and returns the new value.
    """
    logging.info("Counter function triggered: %s", req.method)

    try:
        table_client = get_table_client()

        if req.method == "GET":
            count = get_count(table_client)
        else:
            count = increment_count(table_client)

        return func.HttpResponse(
            body=json.dumps({"count": count}),
            status_code=200,
            mimetype="application/json",
        )

    except Exception as e:
        logging.error("Counter function error: %s", str(e))
        return func.HttpResponse(
            body=json.dumps({"error": "Internal server error"}),
            status_code=500,
            mimetype="application/json",
        )
