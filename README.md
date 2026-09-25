# Waypoint Concierge · AI Trip Planner & Travel Concierge

![Waypoint Concierge Live Demo](./agent_demo.gif)

> 🎬 *Watch the full video recording with AI-generated lo-fi soundtrack: [`agent_demo.webm`](./agent_demo.webm)*

Waypoint Concierge is an intelligent, personalized travel planning assistant built with the **Agent Development Kit (ADK)**, **Gemini 2.5 Flash**, **Vertex AI Agent Engine**, and the **A2A (Agent-to-Agent) Protocol**.

It provides travelers with curated destination discovery, activity suggestions, day-by-day itinerary management, sandboxed budget calculations, scenic postcard generation, and rich interactive A2UI card layouts.

---

## 🛠️ Implemented Features & Google Cloud Services

The capabilities below are fully wired and functional in the codebase:

### 1. Cross-Session Long-Term Memory (Vertex AI Memory Bank)
- **Tool / Callback**: `PreloadMemoryTool` and `generate_memories_callback` in `app/agent.py`.
- **Functionality**: Persists traveler profiles, travel habits, dietary preferences, and allergies across sessions. Proactively verifies and respects dietary restrictions (e.g., peanut allergies, vegetarian diets) in all dining recommendations.

### 2. Destination Catalog & Itinerary Persistence (Google Cloud Firestore)
- **Tools**: `search_destinations`, `get_destination_details`, `save_destination`, `add_to_itinerary`, and `get_itinerary` in `app/firestore_tools.py`.
- **Functionality**: Queries and manages curated destination documents and user itineraries stored in Google Cloud Firestore.

### 3. Image Generation & Asset Storage (Gemini & Google Cloud Storage)
- **Tool**: `generate_destination_image` in `app/image_tool.py`.
- **Model**: `gemini-3.1-flash-lite-image`.
- **Functionality**: Dynamically synthesizes scenic destination postcards and mood board visuals, automatically uploads them to a Google Cloud Storage bucket, and returns public image URLs for inline rendering.

### 4. Sandboxed Code Execution (Vertex AI Agent Engine Sandbox)
- **Executor**: `AgentEngineSandboxCodeExecutor` in `app/agent.py`.
- **Functionality**: Safely executes Python code in an isolated Vertex AI Agent Engine sandbox to compute accurate travel math, daily budget breakdowns, expense allocations, and currency conversions.

### 5. Rich Adaptive UI (A2UI v0.8 Basic Catalog)
- **Callback**: `a2ui_callback` and `A2uiSchemaManager` in `app/a2ui_utils.py`.
- **Functionality**: Generates structured A2UI component trees (`Card`, `Column`, `Row`, `Text`, `Image`) so itineraries, destination cards, and generated postcards render natively in the chat interface rather than plain markdown text.

### 6. Geocoding & Places Discovery (Google Maps & Places APIs)
- **Tools**: `geocode_address` and `search_nearby_places` in `app/maps_tools.py`.
- **Functionality**: Discovers real-world attractions, landmarks, and dining spots near specified destinations with distance radii and address coordinates.

### 7. Weather & Currency Tools
- **Tools**: `get_live_weather` in `app/weather.py` and `convert_currency` in `app/currency.py`.
- **Functionality**: Fetches live temperature and forecast data and converts foreign exchange rates.

### 8. Web Frontend & Proxy (A2A Protocol)
- **Directory**: `frontend/`.
- **Functionality**: Minimal FastAPI proxy and responsive web interface that communicates with the deployed Agent Engine runtime using the open Agent-to-Agent (A2A) protocol. Features custom theme branding, dialogue message styling, and one-click starter prompt chips.

---

## 📋 Planned Capabilities (Not Yet Implemented)

- **Interactive Map Route Visualization**: Dynamic polyline rendering of walking/driving routes between itinerary stops on an interactive map.
- **Direct Reservation Booking**: Direct integration with airline and hotel reservation checkout APIs.

---

## 📁 Repository Structure

```
waypoint-concierge/
├── app/
│   ├── agent.py               # Main agent configuration, memory bank, and tool bindings
│   ├── a2ui_utils.py          # A2UI after_model_callback transformer
│   ├── firestore_tools.py     # Firestore destination catalog & itinerary persistence
│   ├── image_tool.py          # Gemini 3.1 Flash Lite Image generation & GCS uploader
│   ├── maps_tools.py          # Google Places and Geocoding API tools
│   ├── currency.py            # Currency conversion calculations
│   ├── weather.py             # Live destination weather service
│   └── fast_api_app.py        # ADK FastAPI service entrypoint
├── frontend/
│   ├── main.py                # FastAPI proxy connecting browser to agent over A2A
│   ├── static/
│   │   └── index.html         # Responsive Chat UI with A2UI renderer and prompt chips
│   ├── Dockerfile             # Container configuration for Cloud Run
│   └── requirements.txt       # Frontend proxy dependencies
├── agents-cli-manifest.yaml   # Agent Engine deployment manifest
├── pyproject.toml             # Python dependencies and project metadata
└── project_brief.md           # Project specification and requirements
```

---

## 🚀 Running the Project Locally

### Prerequisites

- Python 3.12+
- [`uv`](https://docs.astral.sh/uv/) package manager
- Google Cloud SDK (`gcloud`) authenticated to your Google Cloud project

### 1. Configure Environment

Copy the example environment file and configure your API keys:

```bash
cp .env.example .env
```

Ensure `GOOGLE_MAPS_API_KEY="your_key_here"` is set if utilizing live Google Maps and Places lookups.

### 2. Start the Agent in ADK Playground

Install dependencies and start the local ADK developer environment:

```bash
uv sync
uv run adk web . --port 8080 --reload_agents
```

### 3. Run the Web Frontend

In a separate terminal, start the custom chat frontend proxy:

```bash
cd frontend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

export AGENT_ENGINE_RESOURCE_NAME="projects/<PROJECT_ID>/locations/<LOCATION>/reasoningEngines/<REASONING_ENGINE_ID>"
export AGENT_DIRECTORY="app"
export PORT=8080
python main.py
```

Open your local browser to the host and port specified by the server (default `port 8080`).

---

## 📄 License

Apache License 2.0
