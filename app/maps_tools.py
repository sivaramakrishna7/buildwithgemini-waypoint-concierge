"""Google Maps Geocoding and Places API (New) tools."""

import json
import os
import urllib.parse
import urllib.request
from typing import Any
from dotenv import load_dotenv

load_dotenv()


def _get_api_key() -> str:
    key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not key:
        raise ValueError("GOOGLE_MAPS_API_KEY environment variable is not set.")
    return key


def geocode_address(address: str) -> dict[str, Any]:
    """Turn an address or landmark name into geographic coordinates using Google Geocoding API.

    Args:
        address: The address, city, or landmark to geocode (e.g., '1600 Amphitheatre Pkwy, Mountain View, CA' or 'Taj Mahal, Agra').

    Returns:
        A dictionary with the formatted name, address, and latitude/longitude location.
    """
    try:
        api_key = _get_api_key()
        encoded = urllib.parse.quote(address)
        url = f"https://maps.googleapis.com/maps/api/geocode/json?address={encoded}&key={api_key}"

        req = urllib.request.Request(url, headers={"User-Agent": "WaypointConcierge/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())

        status = data.get("status")
        if status != "OK" or not data.get("results"):
            error_msg = data.get("error_message", f"Geocoding returned status: {status}")
            return {"error": error_msg}

        result = data["results"][0]
        location = result["geometry"]["location"]
        formatted_address = result.get("formatted_address", "")

        return {
            "name": address,
            "address": formatted_address,
            "location": {
                "latitude": location.get("lat"),
                "longitude": location.get("lng"),
            },
        }
    except Exception as e:
        return {"error": f"Failed to geocode address: {str(e)}"}


def search_nearby_places(
    latitude: float,
    longitude: float,
    place_type: str = "restaurant",
    radius_meters: float = 1500.0,
    max_results: int = 5,
) -> list[dict[str, Any]] | dict[str, Any]:
    """Find nearby places of a given type around a coordinate using Places API (New).

    Args:
        latitude: Latitude of the center point (e.g., 37.4220).
        longitude: Longitude of the center point (e.g., -122.0841).
        place_type: Type of place to search for (e.g., 'restaurant', 'cafe', 'museum', 'tourist_attraction', 'lodging', 'bakery').
        radius_meters: Search radius in meters (up to 50000, default 1500.0).
        max_results: Maximum results to return (1 to 20, default 5).

    Returns:
        A list of nearby places with name, address, and location coordinates.
    """
    try:
        api_key = _get_api_key()
        url = "https://places.googleapis.com/v1/places:searchNearby"

        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": api_key,
            "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.location",
            "User-Agent": "WaypointConcierge/1.0",
        }

        # Validate max_results within bounds
        count = max(1, min(int(max_results), 20))
        radius = max(100.0, min(float(radius_meters), 50000.0))

        body = {
            "includedTypes": [place_type.strip().lower()],
            "maxResultCount": count,
            "locationRestriction": {
                "circle": {
                    "center": {
                        "latitude": float(latitude),
                        "longitude": float(longitude),
                    },
                    "radius": radius,
                }
            },
        }

        req = urllib.request.Request(url, data=json.dumps(body).encode("utf-8"), headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())

        raw_places = data.get("places", [])
        results = []
        for p in raw_places:
            results.append({
                "name": p.get("displayName", {}).get("text", "Unknown"),
                "address": p.get("formattedAddress", ""),
                "location": {
                    "latitude": p.get("location", {}).get("latitude"),
                    "longitude": p.get("location", {}).get("longitude"),
                },
            })

        return results
    except Exception as e:
        return {"error": f"Failed to search nearby places: {str(e)}"}
