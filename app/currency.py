"""Currency conversion tool for travel budgeting using the Frankfurter public API."""

import json
import os
import urllib.parse
import urllib.request
from typing import Any

# Optional configuration via environment variable
API_BASE_URL = os.getenv("FRANKFURTER_API_URL", "https://api.frankfurter.dev/v1")


def convert_currency(
    amount: float,
    from_currency: str = "USD",
    to_currency: str = "JPY",
) -> dict[str, Any]:
    """Convert an amount from one currency to another using live foreign exchange rates.

    Args:
        amount: The monetary amount to convert (e.g., 100.0).
        from_currency: 3-letter currency code to convert from (e.g., 'USD', 'EUR', 'GBP'). Defaults to 'USD'.
        to_currency: 3-letter currency code to convert to (e.g., 'JPY', 'INR', 'EUR', 'GBP'). Defaults to 'JPY'.

    Returns:
        A dictionary with the converted amount, exchange rate, and date.
    """
    from_curr = from_currency.strip().upper()
    to_curr = to_currency.strip().upper()

    if from_curr == to_curr:
        return {
            "original_amount": amount,
            "from_currency": from_curr,
            "to_currency": to_curr,
            "converted_amount": amount,
            "rate": 1.0,
        }

    try:
        query_params = urllib.parse.urlencode({
            "amount": amount,
            "base": from_curr,
            "symbols": to_curr,
        })
        url = f"{API_BASE_URL}/latest?{query_params}"
        req = urllib.request.Request(url, headers={"User-Agent": "WaypointConcierge/1.0"})

        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())

        rates = data.get("rates", {})
        converted = rates.get(to_curr)

        if converted is None:
            return {"error": f"Could not find exchange rate for {to_curr} from {from_curr}."}

        unit_rate = converted / amount if amount != 0 else 0.0

        return {
            "original_amount": amount,
            "from_currency": from_curr,
            "to_currency": to_curr,
            "converted_amount": converted,
            "exchange_rate": round(unit_rate, 4),
            "date": data.get("date"),
        }
    except Exception as e:
        return {"error": f"Currency conversion failed: {str(e)}"}
