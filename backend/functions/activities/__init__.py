import json
import os
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from urllib.parse import urlparse

import azure.functions as func
from azure.cosmos import CosmosClient

from shared.validation import validate_activity_payload, Activity
from shared.cosmos_client import get_client, get_db_and_container
from shared.logging import get_logger

logger = get_logger()

PARTITION_KEY_FIELD = os.getenv("COSMOS_PARTITION_KEY", "type")


def _json_response(
    status: int, 
    body: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None
) -> func.HttpResponse:
    """Create JSON response with security headers."""
    default_headers = {
        "Content-Type": "application/json",
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Content-Security-Policy": "default-src 'self'",
    }
    
    if headers:
        default_headers.update(headers)
    
    return func.HttpResponse(
        body=(json.dumps(body) if body is not None else ""),
        status_code=status,
        headers=default_headers,
    )


def _get_container() -> Any:
    client: CosmosClient = get_client()
    _, container = get_db_and_container(client)
    return container


def _query_item_by_id(container, item_id: str) -> Optional[Dict[str, Any]]:
    query = "SELECT * FROM c WHERE c.id = @id"
    params = [{"name": "@id", "value": item_id}]
    items = list(container.query_items(query=query, parameters=params, enable_cross_partition_query=True))
    return items[0] if items else None


def _extract_item_id(req: func.HttpRequest) -> Optional[str]:
    route_params = getattr(req, "route_params", {})
    item_id = route_params.get("id")
    if item_id:
        return item_id
    # Fallback for tests: parse from URL path
    try:
        path = urlparse(req.url).path
        prefix = "/api/activities/"
        if path.startswith(prefix):
            rest = path[len(prefix):]
            return rest or None
    except Exception:
        pass
    return None


def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        method = req.method.upper()
        item_id = _extract_item_id(req)

        container = _get_container()

        if method == "GET":
            # List activities with optional type filter and limit
            type_filter = req.params.get("type")
            limit = req.params.get("limit")
            try:
                limit_val = int(limit) if limit is not None else 50
            except ValueError:
                return _json_response(400, {"error": "Invalid limit"})
            if limit_val < 1 or limit_val > 100:
                return _json_response(400, {"error": "Limit out of range (1-100)"})

            query = "SELECT TOP @limit * FROM c WHERE (@type IS NULL OR c.type = @type) ORDER BY c.date DESC"
            params = [
                {"name": "@limit", "value": limit_val},
                {"name": "@type", "value": type_filter},
            ]
            items = list(container.query_items(query=query, parameters=params, enable_cross_partition_query=True))
            return _json_response(200, items)

        if method == "POST":
            try:
                payload = req.get_json()
            except ValueError:
                return _json_response(400, {"error": "Invalid JSON"})
            try:
                validated = validate_activity_payload(payload)
            except Exception as e:
                return _json_response(400, {"error": str(e)})

            activity = Activity(
                id=str(uuid.uuid4()),
                **validated.model_dump(),
            )
            doc = activity.model_dump()
            container.create_item(body=doc)
            logger.info("Activity created", extra={"id": doc["id"], "type": doc.get("type")})
            return _json_response(201, doc)

        if method == "PUT":
            if not item_id:
                return _json_response(400, {"error": "Missing id in route"})
            existing = _query_item_by_id(container, item_id)
            if not existing:
                return _json_response(404, {"error": "Not found"})
            try:
                payload = req.get_json()
            except ValueError:
                return _json_response(400, {"error": "Invalid JSON"})

            # Merge fields and re-validate as Activity
            merged = existing.copy()
            merged.update(payload)
            try:
                # Reuse base validation via Activity model
                updated = Activity(**merged)
            except Exception as e:
                return _json_response(400, {"error": str(e)})
            updated.updatedAt = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            doc = updated.model_dump()
            # Partition key required for point operations; ensure field present
            pk_val = doc.get(PARTITION_KEY_FIELD)
            container.replace_item(item=item_id, body=doc, partition_key=pk_val)
            logger.info("Activity updated", extra={"id": item_id})
            return _json_response(200, doc)

        if method == "DELETE":
            if not item_id:
                return _json_response(400, {"error": "Missing id in route"})
            existing = _query_item_by_id(container, item_id)
            if not existing:
                return _json_response(404, {"error": "Not found"})
            pk_val = existing.get(PARTITION_KEY_FIELD)
            container.delete_item(item=item_id, partition_key=pk_val)
            logger.info("Activity deleted", extra={"id": item_id})
            return _json_response(204)

        return _json_response(405, {"error": "Method not allowed"})

    except Exception as e:
        logger.error(f"Unhandled error: {e}")
        return _json_response(500, {"error": "Internal server error"})
