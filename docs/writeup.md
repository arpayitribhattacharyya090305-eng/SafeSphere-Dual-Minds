# Kaggle Capstone Write-up

## Problem Statement
Disaster response systems need to combine real-time alerts, shelter logistics, medical guidance, and communication support into one actionable platform during emergencies.

## Innovation
SafeSphere brings together multiple AI agents via LangGraph to collaborate around one user request. The system fuses weather data, OpenStreetMap route planning, Overpass shelter and resource search, medical guidance, and relief information into a coherent rescue plan.

## Architecture
The platform uses Streamlit for the frontend, FastAPI for the backend API, LangGraph for agent orchestration, ChromaDB for medical RAG retrieval, and the OpenStreetMap ecosystem for all mapping. Folium renders maps in Streamlit, Nominatim handles geocoding, Overpass locates nearby emergency resources, and OSRM calculates evacuation routes without any billing-enabled map API.

## Agent Workflow
Coordinator → Vision → Weather → Search → Navigation → Shelter → Medical → Communication → Government → Recovery → Volunteer.

## Evaluation
The solution is evaluated on multi-agent reasoning, practical utility, UI polish, and modular architecture.

## Future Scope
Future upgrades include self-hosted OSRM/Overpass/Nominatim instances for high-volume deployments, additional GIS layers, voice interaction, multilingual speech synthesis, and production PostgreSQL deployment.
