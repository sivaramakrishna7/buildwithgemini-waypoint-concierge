# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import datetime
from zoneinfo import ZoneInfo

from a2ui.basic_catalog.provider import BasicCatalog
from a2ui.schema.manager import A2uiSchemaManager
from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.apps import App
from google.adk.code_executors import AgentEngineSandboxCodeExecutor
from google.adk.models import Gemini
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from google.genai import types

try:
    from app.a2ui_utils import a2ui_callback
    from app.firestore_tools import (
        add_to_itinerary,
        get_destination_details,
        get_itinerary,
        save_destination,
        search_destinations,
    )
    from app.weather import get_live_weather
    from app.currency import convert_currency
    from app.maps_tools import geocode_address, search_nearby_places
    from app.image_tool import generate_destination_image
except ImportError:
    from .a2ui_utils import a2ui_callback
    from .firestore_tools import (
        add_to_itinerary,
        get_destination_details,
        get_itinerary,
        save_destination,
        search_destinations,
    )
    from .weather import get_live_weather
    from .currency import convert_currency
    from .maps_tools import geocode_address, search_nearby_places
    from .image_tool import generate_destination_image


MODEL = "gemini-3.6-flash"

SANDBOX_RESOURCE_NAME = os.getenv(
    "AGENT_ENGINE_SANDBOX_RESOURCE_NAME",
    "projects/758182797445/locations/us-east1/reasoningEngines/447604586597842944/sandboxEnvironments/4878647441651400704",
)

code_executor = AgentEngineSandboxCodeExecutor(
    sandbox_resource_name=SANDBOX_RESOURCE_NAME,
)


def get_weather(query: str) -> str:
    """Simulates a web search. Use it get information on weather.

    Args:
        query: A string containing the location to get weather information for.

    Returns:
        A string with the simulated weather information for the queried location.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        return "It's 60 degrees and foggy."
    return "It's 90 degrees and sunny."


def get_current_time(query: str) -> str:
    """Simulates getting the current time for a city.

    Args:
        city: The name of the city to get the current time for.

    Returns:
        A string with the current time information.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        tz_identifier = "America/Los_Angeles"
    else:
        return f"Sorry, I don't have timezone information for query: {query}."

    tz = ZoneInfo(tz_identifier)
    now = datetime.datetime.now(tz)
    return f"The current time for query {query} is {now.strftime('%Y-%m-%d %H:%M:%S %Z%z')}"


async def generate_memories_callback(callback_context: CallbackContext):
    """Callback after each agent turn to persist and extract memories from the session."""
    await callback_context.add_session_to_memory()
    return None


schema_manager = A2uiSchemaManager(
    version="0.8",
    catalogs=[BasicCatalog.get_config("0.8")],
)

instruction = schema_manager.generate_system_prompt(
    role_description=(
        "You are Waypoint Concierge, a knowledgeable and personalized travel itinerary assistant. "
        "Help travelers discover destinations, explore curated attractions and local spots, "
        "organize trip itineraries using your Firestore travel catalog, and perform calculations "
        "or analysis using your Python sandbox code execution.\n\n"
        "Cross-Session Long-Term Memory:\n"
        "You remember the user's stated preferences, travel habits, dietary restrictions, and allergies "
        "across conversations and sessions to personalize your responses. Pay special attention to all "
        "allergies mentioned by the user: always remember them, strictly avoid recommending foods, dishes, "
        "or dining experiences that contain allergens the user is allergic to, and proactively account for "
        "these allergies in all travel and dining suggestions."
    ),
    workflow_description="Analyze the request and return structured UI when appropriate.",
    ui_description=(
        "Keep every surface tiny and flat: ONE Card > ONE Column > a few Text rows. "
        "Never nest a Card inside a Card. "
        "Use ONLY these components: Card, Column, Row, Text, and Image. Do not use "
        "Table or Heading (unsupported), or Buttons, actions, or forms (they do "
        "nothing in adk web). "
        "You may include one Image component, but only when you have a public https "
        "URL for the image (for example the URL an image tool returns after uploading "
        "to a public bucket). Set the Image url to that exact https link, for example "
        "{\"Image\": {\"url\": {\"literalString\": \"https://...\"}}}. Never point an "
        "Image at a bare filename, an artifact name, or a non-http(s) path. If you do "
        "not have a public URL, add a short Text line noting the image instead. "
        "No markdown in text; use the usageHint property ('h1', 'h2', 'body') for "
        "headings and emphasis. "
        "Output ONLY the raw A2UI JSON array — no prose, and never wrap it in "
        "<a2a_datapart_json> tags or 'kind'/'data'/'metadata' objects."
    ),
    include_schema=True,
    include_examples=True,
)

root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=instruction,
    code_executor=code_executor,
    tools=[
        PreloadMemoryTool(),
        search_destinations,
        get_destination_details,
        save_destination,
        add_to_itinerary,
        get_itinerary,
        get_live_weather,
        convert_currency,
        geocode_address,
        search_nearby_places,
        generate_destination_image,
        get_current_time,
    ],
    after_model_callback=a2ui_callback,
    after_agent_callback=generate_memories_callback,
)

app = App(
    root_agent=root_agent,
    name="app",
)
