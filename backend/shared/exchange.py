"""Helpers for retrieving and validating exchange rate data."""

from __future__ import annotations

import os
from typing import Dict, Optional

import requests


class ExchangeRateProviderError(RuntimeError):
    """Raised when the upstream exchange rate provider reports an error."""


def _get_timeout() -> float:
    try:
        return float(os.environ.get("EXCHANGE_API_TIMEOUT", "5"))
    except (TypeError, ValueError):
        return 5.0


API_BASE_URL = os.environ.get("EXCHANGE_API_BASE", "https://open.er-api.com/v6/latest")
DEFAULT_TIMEOUT = _get_timeout()


def normalize_currency(code: Optional[str]) -> str:
    if not code:
        raise ValueError("Currency code is required")

    normalized = str(code).strip().upper()
    if len(normalized) != 3 or not normalized.isalpha():
        raise ValueError(f"Invalid currency code '{code}'")

    return normalized


def fetch_rates(base_currency: str) -> Dict[str, object]:
    base = normalize_currency(base_currency)
    url = f"{API_BASE_URL}/{base}"

    response = requests.get(url, timeout=DEFAULT_TIMEOUT)
    response.raise_for_status()
    payload = response.json()

    if payload.get("result") == "error":
        error_type = payload.get("error-type", "exchange_rate_error")
        if error_type == "unsupported-code":
            raise ValueError(f"Currency '{base}' is not supported")
        raise ExchangeRateProviderError(f"Exchange rate provider error: {error_type}")

    rates = payload.get("rates") or payload.get("conversion_rates")
    if not isinstance(rates, dict):
        raise ExchangeRateProviderError("Invalid response from exchange rate provider")

    return {
        "base": base,
        "rates": rates,
        "last_updated": payload.get("time_last_update_utc") or payload.get("time_last_update"),
        "next_update": payload.get("time_next_update_utc") or payload.get("time_next_update"),
        "additional_info": {
            "documentation": payload.get("documentation"),
            "terms_of_use": payload.get("terms_of_use"),
        },
    }
