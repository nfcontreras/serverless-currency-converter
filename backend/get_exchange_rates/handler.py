import json

import requests

from shared.exchange import ExchangeRateProviderError, fetch_rates

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


def get_exchange_rates(event, context):
    try:
        params = event.get("queryStringParameters") or {}
        base_currency = params.get("base") or "USD"

        rates_payload = fetch_rates(base_currency)

        return _success_response({
            "success": True,
            "base": rates_payload["base"],
            "rates": rates_payload["rates"],
            "last_updated": rates_payload.get("last_updated"),
            "next_update": rates_payload.get("next_update"),
            "metadata": rates_payload.get("additional_info"),
        })

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
