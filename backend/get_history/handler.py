import json
import logging

from shared.storage import fetch_history

HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Content-Type": "application/json",
}

FALLBACK_HISTORY = [
    {
        "from": "USD",
        "to": "EUR",
        "amount": 100,
        "result": 89,
        "timestamp": "2025-10-28T10:00:00Z",
    },
    {
        "from": "EUR",
        "to": "COP",
        "amount": 50,
        "result": 215000,
        "timestamp": "2025-10-27T14:30:00Z",
    },
]

logger = logging.getLogger(__name__)


def _success_response(body):
    return {
        "statusCode": 200,
        "headers": HEADERS,
        "body": json.dumps(body),
    }


def _error_response(status_code, message, error_detail=None):
    data = {"success": False, "message": message}
    if error_detail is not None:
        data["error"] = error_detail
    return {
        "statusCode": status_code,
        "headers": HEADERS,
        "body": json.dumps(data),
    }


def get_history(event, context):
    try:
        history, storage_active = fetch_history()
        if not history:
            history = FALLBACK_HISTORY

        return _success_response({
            "success": True,
            "history": history,
            "source": "dynamodb" if storage_active else "mock",
        })

    except Exception as exc:
        logger.exception("Error al obtener el historial de conversiones")
        return _error_response(500, "Internal server error", str(exc))
