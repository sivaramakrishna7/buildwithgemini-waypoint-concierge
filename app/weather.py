"""Live weather fetching tool using Open-Meteo API."""

import json
import urllib.parse
import urllib.request
from typing import Any

WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Foggy",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    71: "Slight snow",
    73: "Moderate snow",
    75: "Heavy snow",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    95: "Thunderstorm",
}


def get_live_weather(location: str) -> dict[str, Any]:
    """Fetch real-time current weather and 3-day forecast for any city or destination.

    Args:
        location: City name or destination (e.g., 'Kyoto', 'Paris', 'San Francisco', 'Agra').

    Returns:
        A dictionary with current temperature, conditions, and upcoming forecast.
    """
    try:
        encoded = urllib.parse.quote(location)
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={encoded}&count=1&language=en&format=json"
        req = urllib.request.Request(geo_url, headers={"User-Agent": "WaypointConcierge/1.0"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            geo_data = json.loads(resp.read().decode())

        results = geo_data.get("results")
        if not results:
            return {"error": f"Could not find coordinates for location: {location}"}

        place = results[0]
        lat, lon = place["latitude"], place["longitude"]
        city_name = place.get("name", location)
        country = place.get("country", "")

        forecast_url = (
            f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
            f"&current=temperature_2m,apparent_temperature,weather_code"
            f"&daily=temperature_2m_max,temperature_2m_min,weather_code"
            f"&forecast_days=3&timezone=auto"
        )
        req_forecast = urllib.request.Request(forecast_url, headers={"User-Agent": "WaypointConcierge/1.0"})
        with urllib.request.urlopen(req_forecast, timeout=5) as resp:
            weather_data = json.loads(resp.read().decode())

        current = weather_data.get("current", {})
        code = current.get("weather_code", 0)
        condition = WEATHER_CODES.get(code, "Clear")

        daily = weather_data.get("daily", {})
        dates = daily.get("time", [])
        max_temps = daily.get("temperature_2m_max", [])
        min_temps = daily.get("temperature_2m_min", [])
        codes = daily.get("weather_code", [])

        forecast = []
        for i in range(len(dates)):
            forecast.append({
                "date": dates[i],
                "high_c": max_temps[i],
                "low_c": min_temps[i],
                "condition": WEATHER_CODES.get(codes[i], "Variable"),
            })

        return {
            "location": f"{city_name}, {country}".strip(", "),
            "temperature_c": current.get("temperature_2m"),
            "feels_like_c": current.get("apparent_temperature"),
            "condition": condition,
            "forecast_3_day": forecast,
        }
    except Exception as e:
        return {"error": f"Failed to fetch live weather: {str(e)}"}
