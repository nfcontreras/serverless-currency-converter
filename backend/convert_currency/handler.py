import base64
import json
import logging
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

import requests

from shared.exchange import ExchangeRateProviderError, fetch_rates, normalize_currency
from shared.storage import store_conversion_record

logger = logging.getLogger(__name__)
HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Content-Type": "application/json",
}


def _success_response(payload):
    return {
        "statusCode": 200,
        "headers": HEADERS,
        "body": json.dumps(payload),
    }


def _error_response(status_code, message, error_detail=None):
    body = {"success": False, "message": message}
    if error_detail is not None:
        body["error"] = error_detail
    return {
        "statusCode": status_code,
        "headers": HEADERS,
        "body": json.dumps(body),
    }


def _parse_json_body(event):
    raw_body = event.get("body")
    if raw_body is None:
        raise ValueError("Request body is required")

    if event.get("isBase64Encoded"):
        raw_body = base64.b64decode(raw_body).decode("utf-8")

    try:
        return json.loads(raw_body)
    except (TypeError, json.JSONDecodeError) as exc:
        raise ValueError("Request body must be valid JSON") from exc


def convert_currency(event, context):
    try:
        body = _parse_json_body(event)
        from_currency = normalize_currency(body.get("from"))
        to_currency = normalize_currency(body.get("to"))

        try:
            amount = Decimal(str(body.get("amount")))
        except (InvalidOperation, TypeError):
            return _error_response(400, "'amount' must be a valid number")

        rates_payload = fetch_rates(from_currency)
        rates = rates_payload["rates"]

        if to_currency not in rates:
            return _error_response(400, f"Currency '{to_currency}' is not supported")

        rate = Decimal(str(rates[to_currency]))
        converted = (amount * rate).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        timestamp = datetime.now(timezone.utc).isoformat()

        payload = {
            "success": True,
            "from": from_currency,
            "to": to_currency,
            "amount": float(amount),
            "result": float(converted),
            "rate": float(rate),
            "last_updated": rates_payload.get("last_updated"),
            "timestamp": timestamp,
        }

        try:
            store_conversion_record({
                "from": from_currency,
                "to": to_currency,
                "amount": amount,
                "result": converted,
                "rate": rate,
                "last_updated": rates_payload.get("last_updated"),
                "timestamp": timestamp,
            })
        except Exception as exc:  # pragma: no cover - logging only
            logger.warning("No se pudo guardar el historial de conversiones: %s", exc)

        return _success_response(payload)

    except ValueError as exc:
        return _error_response(400, str(exc))
    except requests.Timeout:
        return _error_response(504, "Exchange rate service timed out")
    except requests.HTTPError as exc:
        return _error_response(exc.response.status_code, "Exchange rate service returned an error", str(exc))
    except requests.RequestException:
        return _error_response(502, "Unable to contact exchange rate service")
    except ExchangeRateProviderError as exc:
        return _error_response(502, str(exc))
    except Exception as exc:
        return _error_response(500, "Internal server error", str(exc))
