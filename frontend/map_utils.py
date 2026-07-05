"""Folium helpers used by RescueAI Streamlit pages."""

from __future__ import annotations

from typing import Iterable, List, Mapping, Sequence

import folium
from folium.plugins import HeatMap

Coordinate = Sequence[float]


def create_osm_map(lat: float, lng: float, zoom_start: int = 13) -> folium.Map:
    """Create an OpenStreetMap-backed Folium map."""
    return folium.Map(location=[lat, lng], zoom_start=zoom_start, tiles="OpenStreetMap")


def add_user_location(
    map_obj: folium.Map,
    lat: float,
    lng: float,
    label: str = "My Location",
) -> None:
    """Draw the user's current location."""
    folium.Marker(
        location=[lat, lng],
        popup=f"<b>{label}</b>",
        tooltip="User location",
        icon=folium.Icon(color="blue", icon="user", prefix="fa"),
    ).add_to(map_obj)
    add_radius_circle(map_obj, lat, lng, radius_m=500, tooltip="500 m radius")


def add_radius_circle(
    map_obj: folium.Map,
    lat: float,
    lng: float,
    radius_m: int,
    tooltip: str = "Search radius",
) -> None:
    """Draw a radius search circle around a coordinate."""
    folium.Circle(
        location=[lat, lng],
        radius=radius_m,
        color="#2563eb",
        fill=True,
        fill_opacity=0.08,
        tooltip=tooltip,
    ).add_to(map_obj)


def add_place_markers(
    map_obj: folium.Map,
    places: Iterable[Mapping[str, object]],
    color: str,
    icon: str,
    tooltip: str,
) -> None:
    """Draw standard markers for shelters, hospitals, and resource points."""
    for place in places:
        lat = place.get("location_lat")
        lng = place.get("location_lng")
        if lat is None or lng is None:
            continue
        name = str(place.get("name") or tooltip)
        address = str(place.get("address") or "OpenStreetMap location")
        distance = place.get("distance_km")
        popup = f"<b>{name}</b><br>{address}"
        if distance is not None:
            popup += f"<br>{distance} km away"
        folium.Marker(
            location=[float(lat), float(lng)],
            popup=popup,
            tooltip=tooltip,
            icon=folium.Icon(color=color, icon=icon, prefix="fa"),
        ).add_to(map_obj)


def add_route(
    map_obj: folium.Map,
    coordinates: List[Coordinate],
    color: str = "#0f766e",
    tooltip: str = "Evacuation route",
) -> None:
    """Draw an OSRM route on a Folium map."""
    if not coordinates:
        return
    folium.PolyLine(
        locations=coordinates,
        color=color,
        weight=6,
        opacity=0.85,
        tooltip=tooltip,
    ).add_to(map_obj)


def add_disaster_zones(
    map_obj: folium.Map,
    incidents: Iterable[Mapping[str, object]],
) -> None:
    """Visualize incident locations with markers and risk-radius circles."""
    severity_colors = {
        "Critical": "#dc2626",
        "High": "#ef4444",
        "Medium": "#f59e0b",
        "Low": "#22c55e",
    }
    for incident in incidents:
        lat = incident.get("location_lat")
        lng = incident.get("location_lng")
        if lat is None or lng is None:
            continue
        severity = str(incident.get("severity") or "Medium")
        color = severity_colors.get(severity, "#f59e0b")
        title = str(incident.get("title") or "Reported incident")
        folium.Marker(
            location=[float(lat), float(lng)],
            popup=f"<b>{title}</b><br>Severity: {severity}",
            tooltip="Disaster zone",
            icon=folium.Icon(
                color="red" if severity in {"Critical", "High"} else "orange",
                icon="exclamation-triangle",
                prefix="fa",
            ),
        ).add_to(map_obj)
        folium.Circle(
            location=[float(lat), float(lng)],
            radius=700 if severity in {"Critical", "High"} else 350,
            color=color,
            fill=True,
            fill_opacity=0.12,
        ).add_to(map_obj)


def add_heatmap(map_obj: folium.Map, points: List[Coordinate]) -> None:
    """Draw a heatmap for dense incident or demand points."""
    if points:
        HeatMap(points, radius=18, blur=14).add_to(map_obj)
