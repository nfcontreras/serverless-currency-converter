"""Optional persistence helpers for conversion history."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple

try:
    import boto3
    from boto3.dynamodb.conditions import Key
    from botocore.exceptions import BotoCoreError, ClientError
except ImportError:  # pragma: no cover - boto3 is optional during local runs
    boto3 = None  # type: ignore[assignment]
    Key = None  # type: ignore[assignment]

    class BotoCoreError(Exception):
        """Fallback exception when botocore is not available."""

    class ClientError(Exception):
        """Fallback exception when botocore is not available."""


logger = logging.getLogger(__name__)

TABLE_NAME = "aws-currency-converter-history"
PARTITION_KEY = "pk"
SORT_KEY = "sk"

_cached_table = None
_table_checked = False


def storage_supported() -> bool:
    return boto3 is not None and Key is not None


def _get_table():
    global _cached_table, _table_checked
    if _cached_table is not None:
        return _cached_table

    if _table_checked or not storage_supported():
        return None

    try:
        resource = boto3.resource("dynamodb")  # type: ignore[union-attr]
        table = resource.Table(TABLE_NAME)
        table.load()  # Ensures the table exists and we have permissions.
    except (BotoCoreError, ClientError) as exc:
        logger.warning("Historial de conversiones deshabilitado: %s", exc)
        _table_checked = True
        return None

    _cached_table = table
    _table_checked = True
    return table


def store_conversion_record(record: Dict[str, Any]) -> bool:
    table = _get_table()
    if table is None:
        return False

    timestamp = record.get("timestamp") or datetime.now(timezone.utc).isoformat()

    item = {
        PARTITION_KEY: "conversion#history",
        SORT_KEY: timestamp,
        "from": record.get("from"),
        "to": record.get("to"),
        "amount": _to_decimal(record.get("amount")),
        "result": _to_decimal(record.get("result")),
        "rate": _to_decimal(record.get("rate")),
        "last_updated": record.get("last_updated"),
    }

    try:
        table.put_item(Item=item)
        return True
    except (BotoCoreError, ClientError) as exc:
        logger.warning("No fue posible guardar el historial: %s", exc)
        return False


def fetch_history(limit: int = 20) -> Tuple[List[Dict[str, Any]], bool]:
    table = _get_table()
    if table is None or not storage_supported():
        return ([], False)

    try:
        response = table.query(
            KeyConditionExpression=Key(PARTITION_KEY).eq("conversion#history"),
            ScanIndexForward=False,
            Limit=limit,
        )
    except (BotoCoreError, ClientError) as exc:
        logger.warning("No fue posible leer el historial: %s", exc)
        return ([], False)

    items = response.get("Items", [])
    history = [
        {
            "from": item.get("from"),
            "to": item.get("to"),
            "amount": _to_float(item.get("amount")),
            "result": _to_float(item.get("result")),
            "rate": _to_float(item.get("rate")),
            "timestamp": item.get(SORT_KEY),
            "last_updated": item.get("last_updated"),
        }
        for item in items
    ]

    return (history, True)


def _to_decimal(value: Any) -> Optional[Decimal]:
    if value is None:
        return None
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


def _to_float(value: Any) -> Optional[float]:
    if value is None:
        return None
    if isinstance(value, Decimal):
        return float(value)
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
