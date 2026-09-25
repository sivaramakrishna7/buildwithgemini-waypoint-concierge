"""Seed script for Waypoint Concierge Firestore catalog.

Populates initial curated destinations matching the project brief.
"""

from google.cloud import firestore

# Hardcoded project ID as string
FIRESTORE_PROJECT_ID = "qwiklabs-gcp-04-793c4bc8c9f7"

SAMPLE_DESTINATIONS = [
    {
        "id": "kyoto-fushimi-inari",
        "name": "Fushimi Inari Taisha",
        "city": "Kyoto",
        "country": "Japan",
        "category": "Culture & Heritage",
        "description": "Iconic Shinto shrine famous for thousands of vibrant vermilion torii gates winding up sacred Mount Inari.",
        "vibes": ["historic", "serene", "photography", "hiking"],
        "cost_tier": "Free",
        "estimated_duration_hours": 2.5,
        "best_time_to_visit": "Early Morning (before 7 AM)",
    },
    {
        "id": "sf-golden-gate-trail",
        "name": "Golden Gate Overlook & Coastal Trail",
        "city": "San Francisco",
        "country": "USA",
        "category": "Scenic Outdoors",
        "description": "Dramatic clifftop trail offering panoramic Pacific views, cypress groves, and classic vistas of the Golden Gate Bridge.",
        "vibes": ["scenic", "ocean-views", "photography", "walking"],
        "cost_tier": "Free",
        "estimated_duration_hours": 2.0,
        "best_time_to_visit": "Late Afternoon / Golden Hour",
    },
    {
        "id": "paris-montmartre-sacrecour",
        "name": "Montmartre & Sacré-Cœur Basilica",
        "city": "Paris",
        "country": "France",
        "category": "Culture & Heritage",
        "description": "Bohemian hilltop district with cobblestone alleys, bustling artist squares, vintage bistros, and sweeping city views.",
        "vibes": ["romantic", "artistic", "panoramic-views", "cafes"],
        "cost_tier": "Free",
        "estimated_duration_hours": 3.0,
        "best_time_to_visit": "Sunset",
    },
    {
        "id": "tokyo-shibuya-sky",
        "name": "Shibuya Sky Observation Deck",
        "city": "Tokyo",
        "country": "Japan",
        "category": "Modern & Urban",
        "description": "Futuristic 360-degree open-air rooftop observatory 229 meters above Shibuya Crossing.",
        "vibes": ["futuristic", "cityscape", "nightlife", "observation-deck"],
        "cost_tier": "$$",
        "estimated_duration_hours": 1.5,
        "best_time_to_visit": "Twilight / Dusk",
    },
    {
        "id": "amalfi-path-of-gods",
        "name": "Sentiero degli Dei (Path of the Gods)",
        "city": "Amalfi Coast",
        "country": "Italy",
        "category": "Scenic Outdoors",
        "description": "World-renowned clifftop hiking trail between Bomerano and Nocelle high above the Mediterranean Sea.",
        "vibes": ["coastal", "hiking", "breathtaking", "nature"],
        "cost_tier": "Free",
        "estimated_duration_hours": 4.0,
        "best_time_to_visit": "Morning",
    },
    {
        "id": "nyc-high-line",
        "name": "The High Line & Chelsea Market",
        "city": "New York City",
        "country": "USA",
        "category": "Scenic Outdoors & Urban",
        "description": "1.45-mile elevated park created on a former rail line, featuring lush gardens, art installations, and access to food stalls.",
        "vibes": ["walking", "art", "parks", "food-stalls"],
        "cost_tier": "Free",
        "estimated_duration_hours": 2.0,
        "best_time_to_visit": "Late Morning",
    },
]


def seed_database():
    print(f"Connecting to Firestore with project: '{FIRESTORE_PROJECT_ID}'...")
    db = firestore.Client(project=FIRESTORE_PROJECT_ID)
    collection = db.collection("destinations")

    count = 0
    for dest in SAMPLE_DESTINATIONS:
        doc_id = dest["id"]
        doc_data = {k: v for k, v in dest.items() if k != "id"}
        collection.document(doc_id).set(doc_data, merge=True)
        print(f"  ✓ Seeded destination: {dest['name']} ({dest['city']}, {dest['country']})")
        count += 1

    print(f"\n🎉 Successfully seeded {count} destinations into Firestore collection 'destinations'!")


if __name__ == "__main__":
    seed_database()
