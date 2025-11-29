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
        # Configuración para desarrollo local
        import os
        if os.environ.get('IS_OFFLINE') or os.environ.get('AWS_SAM_LOCAL'):
            resource = boto3.resource(
                "dynamodb",
                endpoint_url="http://localhost:8000",
                region_name="localhost",
                aws_access_key_id="fake",
                aws_secret_access_key="fake"
            )
        else:
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
            "id": item.get(SORT_KEY),  # timestamp as unique ID
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


def get_conversion_by_id(conversion_id: str) -> Tuple[Optional[Dict[str, Any]], bool]:
    """Obtiene una conversión específica por su ID (timestamp)."""
    table = _get_table()
    if table is None or not storage_supported():
        return (None, False)

    try:
        response = table.get_item(
            Key={
                PARTITION_KEY: "conversion#history",
                SORT_KEY: conversion_id
            }
        )
    except (BotoCoreError, ClientError) as exc:
        logger.warning("No fue posible obtener la conversión: %s", exc)
        return (None, False)

    item = response.get("Item")
    if not item:
        return (None, True)  # No encontrado pero operación exitosa

    conversion = {
        "id": item.get(SORT_KEY),
        "from": item.get("from"),
        "to": item.get("to"),
        "amount": _to_float(item.get("amount")),
        "result": _to_float(item.get("result")),
        "rate": _to_float(item.get("rate")),
        "timestamp": item.get(SORT_KEY),
        "last_updated": item.get("last_updated"),
    }

    return (conversion, True)


def update_conversion_record(conversion_id: str, updates: Dict[str, Any]) -> bool:
    """Actualiza una conversión existente."""
    table = _get_table()
    if table is None:
        return False

    # Primero verificar que la conversión existe
    try:
        response = table.get_item(
            Key={
                PARTITION_KEY: "conversion#history",
                SORT_KEY: conversion_id
            }
        )
        if "Item" not in response:
            return False  # No existe la conversión
    except (BotoCoreError, ClientError) as exc:
        logger.warning("Error verificando la conversión existente: %s", exc)
        return False

    # Construir la expresión de actualización
    update_expression = "SET "
    expression_attribute_values = {}
    expression_parts = []

    allowed_fields = ["from", "to", "amount", "result", "rate", "last_updated"]
    
    for field, value in updates.items():
        if field in allowed_fields:
            expression_parts.append(f"{field} = :{field}")
            if field in ["amount", "result", "rate"]:
                expression_attribute_values[f":{field}"] = _to_decimal(value)
            else:
                expression_attribute_values[f":{field}"] = value

    if not expression_parts:
        return False  # No hay campos válidos para actualizar

    update_expression += ", ".join(expression_parts)

    try:
        table.update_item(
            Key={
                PARTITION_KEY: "conversion#history",
                SORT_KEY: conversion_id
            },
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values
        )
        return True
    except (BotoCoreError, ClientError) as exc:
        logger.warning("No fue posible actualizar la conversión: %s", exc)
        return False


def delete_conversion_record(conversion_id: str) -> bool:
    """Elimina una conversión del historial."""
    table = _get_table()
    if table is None:
        return False

    try:
        table.delete_item(
            Key={
                PARTITION_KEY: "conversion#history",
                SORT_KEY: conversion_id
            }
        )
        return True
    except (BotoCoreError, ClientError) as exc:
        logger.warning("No fue posible eliminar la conversión: %s", exc)
        return False


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
