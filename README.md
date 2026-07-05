# RescueAI

RescueAI is a multi-agent disaster response platform built with FastAPI,
Streamlit, LangGraph, and Gemini. It combines weather intelligence, vision
analysis, OpenStreetMap navigation, shelter lookup, first-aid guidance,
resource discovery, and relief support into one emergency response workflow.

## Highlights

- Multi-agent orchestration with LangGraph
- Vision-based damage assessment workflow
- Weather and live advisory integrations
- RAG-based medical guidance
- OpenStreetMap-based maps with no billing account required
- OSRM evacuation routing with distance, ETA, geometry, and alternatives
- Overpass API nearby search for shelters, hospitals, pharmacies, water,
  food, charging stations, police stations, and fire stations
- Folium maps embedded in Streamlit with `streamlit-folium`
- SQLite-backed demo data with PostgreSQL-ready configuration

## Mapping Architecture

RescueAI uses only the OpenStreetMap ecosystem for maps, places, geocoding, and
directions. No map API key is required.

| Capability | Service |
| --- | --- |
| Base maps | OpenStreetMap |
| Streamlit map rendering | Folium and Streamlit-Folium |
| Geocoding and reverse geocoding | Geopy with Nominatim |
| Nearby emergency place search | Overpass API |
| Routing, distance, ETA, route geometry | OSRM |
| Local resilience | Seeded SQLite fallback data |

The backend mapping classes live in `backend/app/services/maps_service.py`:

- `MapService`
- `GeocodingService`
- `NearbySearchService`
- `RoutingService`

The frontend map helpers live in `frontend/map_utils.py`.

## Quick Start

1. Create and activate a Python virtual environment.

   ```bash
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   ```

2. Install dependencies.

   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment variables in `.env`.

   ```env
   DATABASE_URL=sqlite:///./disaster_response.db
   GEMINI_API_KEY=
   OPENWEATHER_API_KEY=
   TAVILY_API_KEY=
   BACKEND_URL=http://localhost:8000
   ENVIRONMENT=development
   ```

   Maps do not require an API key. Keep only `GEMINI_API_KEY`,
   `OPENWEATHER_API_KEY`, and `TAVILY_API_KEY` for optional live integrations.

4. Run the backend API server.

   ```bash
   uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
   ```

5. In a new terminal, run the Streamlit frontend.

   ```bash
   streamlit run frontend/app.py
   ```

6. Open the app in your browser.

   - Streamlit UI: http://localhost:8501
   - Backend Swagger docs: http://localhost:8000/docs

## Docker

Run both backend and frontend together:

```bash
docker compose up --build
```

## Project Structure

- `backend/` - FastAPI services, API routers, agents, and models
- `backend/app/services/maps_service.py` - OSM, Nominatim, Overpass, and OSRM services
- `frontend/` - Streamlit pages and styling
- `frontend/map_utils.py` - Folium helper utilities
- `docs/` - architecture notes, writeup, and demo script
- `tests/` - smoke and integration tests

## Deployment Notes

- No billing-enabled map service is required.
- The public Overpass, Nominatim, and OSRM endpoints are suitable for demos and
  moderate use. For high-volume production deployments, self-host Overpass,
  Nominatim, or OSRM while keeping the same service interfaces.
- Use PostgreSQL by changing `DATABASE_URL`.
- Keep API keys only for Gemini, OpenWeather, and Tavily when those live
  integrations are needed.


## Authors
- Arpayitri Bhattacharyya
- Chayan Maity