"""Firestore backend and tools for Waypoint Concierge."""

from typing import Any
from google.cloud import firestore

# IMPORTANT: Hardcoded project ID as string.
# Do NOT use google.auth.default() or GOOGLE_CLOUD_PROJECT because on
# Agent Platform those return the numeric project number, breaking Firestore.
FIRESTORE_PROJECT_ID = "qwiklabs-gcp-04-793c4bc8c9f7"

_db: firestore.Client | None = None


def get_db() -> firestore.Client:
    global _db
    if _db is None:
        _db = firestore.Client(project=FIRESTORE_PROJECT_ID)
    return _db


def search_destinations(
    city: str = "", category: str = "", vibe: str = "", limit: int = 10
) -> list[dict[str, Any]]:
    """Search and browse curated travel destinations and attractions.

    Args:
        city: Optional city name to filter by (e.g., 'Tokyo', 'San Francisco', 'Paris').
        category: Optional category (e.g., 'Scenic Outdoors', 'Culture & Heritage', 'Food & Dining').
        vibe: Optional vibe/tag to match (e.g., 'scenic', 'romantic', 'historic', 'cityscape').
        limit: Maximum number of results to return (default 10).

    Returns:
        A list of matching destination summaries.
    """
    db = get_db()
    docs = db.collection("destinations").limit(limit * 2).stream()

    results = []
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        if city and city.lower() not in data.get("city", "").lower():
            continue
        if category and category.lower() not in data.get("category", "").lower():
            continue
        if vibe and not any(vibe.lower() in v.lower() for v in data.get("vibes", [])):
            continue
        results.append(data)
        if len(results) >= limit:
            break
    return results


def get_destination_details(destination_id: str) -> dict[str, Any]:
    """Retrieve full details for a specific destination by its ID.

    Args:
        destination_id: The unique ID of the destination (e.g., 'kyoto-fushimi-inari').

    Returns:
        Destination details or an error message dict if not found.
    """
    db = get_db()
    doc = db.collection("destinations").document(destination_id).get()
    if not doc.exists:
        return {"error": f"Destination with ID '{destination_id}' was not found."}
    data = doc.to_dict()
    data["id"] = doc.id
    return data


def save_destination(
    destination_id: str,
    name: str,
    city: str,
    country: str,
    category: str,
    description: str,
    vibes: list[str],
    cost_tier: str = "$$",
    estimated_duration_hours: float = 2.0,
    best_time_to_visit: str = "Morning",
) -> str:
    """Save or update a destination in the travel catalog.

    Args:
        destination_id: Unique slug ID (e.g., 'rome-colosseum').
        name: Full name of the attraction or spot.
        city: City where it is located.
        country: Country where it is located.
        category: Category (e.g., 'Culture & Heritage', 'Scenic Outdoors', 'Food & Dining').
        description: Informative description of the destination.
        vibes: List of vibe tags (e.g., ['historic', 'iconic', 'architecture']).
        cost_tier: Price level ('Free', '$', '$$', '$$$').
        estimated_duration_hours: Suggested time to spend there in hours.
        best_time_to_visit: Best time of day (e.g., 'Morning', 'Sunset', 'Evening').

    Returns:
        Confirmation message.
    """
    db = get_db()
    doc_ref = db.collection("destinations").document(destination_id)
    payload = {
        "name": name,
        "city": city,
        "country": country,
        "category": category,
        "description": description,
        "vibes": vibes,
        "cost_tier": cost_tier,
        "estimated_duration_hours": estimated_duration_hours,
        "best_time_to_visit": best_time_to_visit,
    }
    doc_ref.set(payload, merge=True)
    return f"Successfully saved destination '{name}' ({destination_id}) in {city}, {country}."


def add_to_itinerary(
    trip_name: str,
    day_number: int,
    place_name: str,
    notes: str = "",
    estimated_duration_hours: float = 2.0,
) -> str:
    """Add a planned spot or activity to a traveler's trip itinerary.

    Args:
        trip_name: Name or identifier of the trip (e.g., 'japan-autumn', 'sf-weekend').
        day_number: Day of the trip (1, 2, 3, etc.).
        place_name: Name of the attraction or activity.
        notes: Helpful notes, tips, or reservations.
        estimated_duration_hours: Estimated duration for this stop.

    Returns:
        Confirmation string.
    """
    db = get_db()
    itinerary_ref = db.collection("itineraries").document(trip_name)
    doc = itinerary_ref.get()
    stops = []
    if doc.exists:
        stops = doc.to_dict().get("stops", [])

    stops.append({
        "day": day_number,
        "place_name": place_name,
        "notes": notes,
        "duration_hours": estimated_duration_hours,
    })
    stops.sort(key=lambda s: s.get("day", 1))
    itinerary_ref.set({"trip_name": trip_name, "stops": stops}, merge=True)
    return f"Added '{place_name}' to Day {day_number} of trip '{trip_name}'."


def get_itinerary(trip_name: str) -> dict[str, Any]:
    """Retrieve the planned itinerary for a given trip.

    Args:
        trip_name: Name of the trip (e.g., 'japan-autumn').

    Returns:
        The itinerary stops and schedule.
    """
    db = get_db()
    doc = db.collection("itineraries").document(trip_name).get()
    if not doc.exists:
        return {"trip_name": trip_name, "stops": [], "message": f"No itinerary found for '{trip_name}' yet."}
    return doc.to_dict()
