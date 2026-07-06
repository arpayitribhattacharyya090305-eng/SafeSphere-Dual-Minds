# SafeSphere Architecture

## Components

- Frontend: Streamlit dashboard for citizen and responder workflows.
- Map UI: Folium maps embedded with Streamlit-Folium and OpenStreetMap tiles.
- Backend: FastAPI REST API and orchestration layer.
- Agents: LangGraph nodes for vision, weather, navigation, sheltering, medical,
  resources, communication, relief, recovery, and volunteering.
- Mapping Services: Nominatim geocoding, Overpass nearby search, and OSRM
  routing through reusable service classes.
- RAG Layer: ChromaDB-backed guideline retrieval for medical and safety
  knowledge.
- Data Layer: SQLite by default, with PostgreSQL-ready configuration.

## OpenStreetMap Service Layer

`backend/app/services/maps_service.py` contains the full keyless mapping stack:

- `MapService`: builds Folium maps and adds markers, polygons, heatmaps,
  disaster zones, shelter markers, hospital markers, user location, and routes.
- `GeocodingService`: converts addresses to coordinates and reverse geocodes
  coordinates with Geopy and Nominatim, including retry logic.
- `NearbySearchService`: searches Overpass API for hospitals, shelters, police
  stations, fire stations, pharmacies, food sources, water points, and charging
  stations.
- `RoutingService`: calculates evacuation routes, driving distance, estimated
  travel time, route geometry, and alternative routes with OSRM.

No billing-enabled map, places, geocoding, or directions APIs are used. The
application does not need a map provider key or billing-enabled map account.

## Request Flow

1. The Streamlit frontend collects disaster information and optional image
   uploads.
2. The FastAPI backend routes requests to the LangGraph workflow.
3. Specialized agent nodes enrich the response with weather, OpenStreetMap
   routing, Overpass place search, shelter data, medical guidance, and live
   search results.
4. The coordinator aggregates the results into a concise action plan.
5. The Streamlit maps page renders user location, disaster zones, shelters,
   hospitals, heatmaps, and OSRM routes with Folium.

## Resilience

The public Overpass, Nominatim, and OSRM endpoints can be rate-limited or
temporarily unavailable. SafeSphere keeps seeded local shelter, hospital, and
resource data as a fallback so emergency pages and agent responses continue to
work during external service interruptions.

For heavy production traffic, deploy self-hosted Nominatim, Overpass, and OSRM
instances and update the service base URLs without changing the agent or API
contracts.

## Deployment

The project supports Docker-based local deployment and production hosting. It
requires API keys only for optional non-map integrations:

- `GEMINI_API_KEY`
- `OPENWEATHER_API_KEY`
- `TAVILY_API_KEY`
