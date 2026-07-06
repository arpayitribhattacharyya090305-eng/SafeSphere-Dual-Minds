"""Free and open-source mapping services for SafeSphere.

This module implements SafeSphere mapping with the OpenStreetMap ecosystem:
Nominatim for geocoding, Overpass API for nearby places, OSRM for routing, and
Folium for map rendering helpers.
"""

from __future__ import annotations

import logging
import math
import time
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional, Tuple

import requests

logger = logging.getLogger(__name__)

Coordinate = Tuple[float, float]


def haversine_distance_km(
    origin_lat: float,
    origin_lng: float,
    dest_lat: float,
    dest_lng: float,
) -> float:
    """Return direct distance between two coordinates in kilometers."""
    radius_km = 6371.0
    lat1 = math.radians(origin_lat)
    lon1 = math.radians(origin_lng)
    lat2 = math.radians(dest_lat)
    lon2 = math.radians(dest_lng)
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(radius_km * c, 2)


@dataclass(frozen=True)
class OverpassPlaceSpec:
    """Describes an Overpass search category."""

    category: str
    tags: Tuple[Tuple[str, str], ...]
    default_quantity: float = 1.0
    default_unit: str = "site"


class GeocodingService:
    """Geocode and reverse-geocode addresses with Nominatim."""

    def __init__(
        self,
        user_agent: str = "safesphere-disaster-response/1.0",
        timeout: int = 10,
        retries: int = 2,
        pause_seconds: float = 1.0,
    ) -> None:
        self.user_agent = user_agent
        self.timeout = timeout
        self.retries = retries
        self.pause_seconds = pause_seconds

    def geocode(self, address: str) -> Dict[str, Any]:
        """Convert an address to latitude/longitude using Nominatim."""
        if not address or not address.strip():
            raise ValueError("Address is required for geocoding.")

        try:
            from geopy.geocoders import Nominatim
            from geopy.exc import GeocoderServiceError, GeocoderTimedOut
        except ImportError as exc:
            raise RuntimeError("geopy is required for Nominatim geocoding.") from exc

        geolocator = Nominatim(user_agent=self.user_agent, timeout=self.timeout)
        last_error: Optional[Exception] = None
        for attempt in range(self.retries + 1):
            try:
                location = geolocator.geocode(address)
                if not location:
                    raise LookupError(f"No coordinates found for '{address}'.")
                return {
                    "lat": float(location.latitude),
                    "lng": float(location.longitude),
                    "address": location.address,
                    "provider": "nominatim",
                }
            except (GeocoderTimedOut, GeocoderServiceError, LookupError) as exc:
                last_error = exc
                logger.warning("Nominatim geocode failed on attempt %s: %s", attempt + 1, exc)
                if attempt < self.retries:
                    time.sleep(self.pause_seconds * (attempt + 1))

        raise RuntimeError(f"Unable to geocode address: {address}") from last_error

    def reverse_geocode(self, lat: float, lng: float) -> Dict[str, Any]:
        """Convert latitude/longitude into a human-readable address."""
        try:
            from geopy.geocoders import Nominatim
            from geopy.exc import GeocoderServiceError, GeocoderTimedOut
        except ImportError as exc:
            raise RuntimeError("geopy is required for Nominatim reverse geocoding.") from exc

        geolocator = Nominatim(user_agent=self.user_agent, timeout=self.timeout)
        last_error: Optional[Exception] = None
        for attempt in range(self.retries + 1):
            try:
                location = geolocator.reverse((lat, lng), exactly_one=True)
                if not location:
                    raise LookupError(f"No address found for {lat}, {lng}.")
                return {
                    "lat": float(lat),
                    "lng": float(lng),
                    "address": location.address,
                    "provider": "nominatim",
                }
            except (GeocoderTimedOut, GeocoderServiceError, LookupError) as exc:
                last_error = exc
                logger.warning(
                    "Nominatim reverse geocode failed on attempt %s: %s",
                    attempt + 1,
                    exc,
                )
                if attempt < self.retries:
                    time.sleep(self.pause_seconds * (attempt + 1))

        raise RuntimeError(f"Unable to reverse geocode coordinates: {lat}, {lng}") from last_error


class RoutingService:
    """Route planning with the public OSRM service."""

    def __init__(
        self,
        base_url: str = "https://router.project-osrm.org",
        timeout: int = 12,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def calculate_route(
        self,
        origin_lat: float,
        origin_lng: float,
        dest_lat: float,
        dest_lng: float,
        profile: str = "driving",
        alternatives: bool = True,
    ) -> Dict[str, Any]:
        """Calculate distance, ETA, route geometry, and steps with OSRM."""
        url = (
            f"{self.base_url}/route/v1/{profile}/"
            f"{origin_lng},{origin_lat};{dest_lng},{dest_lat}"
        )
        params = {
            "overview": "full",
            "geometries": "geojson",
            "steps": "true",
            "alternatives": "true" if alternatives else "false",
        }

        try:
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            routes = data.get("routes") or []
            if not routes:
                raise RuntimeError(data.get("message", "OSRM returned no routes."))
            return self._format_osrm_response(routes)
        except Exception as exc:
            logger.warning("OSRM routing failed; using local route fallback: %s", exc)
            return self._fallback_route(origin_lat, origin_lng, dest_lat, dest_lng)

    def _format_osrm_response(self, routes: List[Dict[str, Any]]) -> Dict[str, Any]:
        primary = routes[0]
        coords = primary.get("geometry", {}).get("coordinates", [])
        polyline_coords = [[lat, lng] for lng, lat in coords]
        legs = primary.get("legs", [])
        steps = self._extract_steps(legs)
        alternative_routes = [
            {
                "distance_km": round(route.get("distance", 0) / 1000, 2),
                "duration_min": round(route.get("duration", 0) / 60, 1),
                "polyline_coords": [
                    [lat, lng]
                    for lng, lat in route.get("geometry", {}).get("coordinates", [])
                ],
            }
            for route in routes[1:]
        ]

        return {
            "distance_km": round(primary.get("distance", 0) / 1000, 2),
            "duration_min": round(primary.get("duration", 0) / 60, 1),
            "steps": steps,
            "polyline_coords": polyline_coords,
            "alternative_routes": alternative_routes,
            "provider": "osrm",
        }

    @staticmethod
    def _extract_steps(legs: Iterable[Dict[str, Any]]) -> List[str]:
        steps: List[str] = []
        for leg in legs:
            for step in leg.get("steps", []):
                maneuver = step.get("maneuver", {})
                action = maneuver.get("type", "continue").replace("_", " ").title()
                road = step.get("name") or "unnamed road"
                distance = round(step.get("distance", 0) / 1000, 2)
                steps.append(f"{action} on {road} for {distance} km.")
        return steps or ["Follow the highlighted OSRM route to the destination."]

    @staticmethod
    def _fallback_route(
        origin_lat: float,
        origin_lng: float,
        dest_lat: float,
        dest_lng: float,
    ) -> Dict[str, Any]:
        distance_km = max(haversine_distance_km(origin_lat, origin_lng, dest_lat, dest_lng) * 1.25, 0.1)
        duration_min = round((distance_km / 25.0) * 60.0, 1)
        polyline_coords = []
        for idx in range(16):
            ratio = idx / 15
            polyline_coords.append(
                [
                    origin_lat + ratio * (dest_lat - origin_lat),
                    origin_lng + ratio * (dest_lng - origin_lng),
                ]
            )
        return {
            "distance_km": round(distance_km, 2),
            "duration_min": duration_min,
            "steps": [
                "OSRM is unavailable. Use the displayed approximate route as a backup.",
                "Move toward the destination while following local emergency instructions.",
            ],
            "polyline_coords": polyline_coords,
            "alternative_routes": [],
            "provider": "local-fallback",
        }


class NearbySearchService:
    """Nearby place search using Overpass API."""

    OVERPASS_URL = "https://overpass-api.de/api/interpreter"
    PLACE_SPECS: Dict[str, OverpassPlaceSpec] = {
        "hospital": OverpassPlaceSpec("Medicine", (("amenity", "hospital"), ("amenity", "clinic"))),
        "shelter": OverpassPlaceSpec(
            "Shelter",
            (
                ("amenity", "shelter"),
                ("social_facility", "shelter"),
                ("emergency", "assembly_point"),
            ),
        ),
        "police": OverpassPlaceSpec("Police", (("amenity", "police"),)),
        "fire_station": OverpassPlaceSpec("Fire Station", (("amenity", "fire_station"),)),
        "pharmacy": OverpassPlaceSpec("Medicine", (("amenity", "pharmacy"),)),
        "food": OverpassPlaceSpec(
            "Food",
            (("amenity", "food_court"), ("shop", "supermarket"), ("shop", "convenience")),
            default_unit="source",
        ),
        "water": OverpassPlaceSpec(
            "Water",
            (("amenity", "drinking_water"), ("man_made", "water_tap")),
            default_unit="point",
        ),
        "charging": OverpassPlaceSpec(
            "Power",
            (("amenity", "charging_station"),),
            default_unit="station",
        ),
    }

    def __init__(self, timeout: int = 20) -> None:
        self.timeout = timeout

    def search(
        self,
        lat: float,
        lng: float,
        place_type: str,
        radius_m: int = 5000,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """Search nearby OSM places for a supported category."""
        spec = self.PLACE_SPECS.get(place_type)
        if not spec:
            raise ValueError(f"Unsupported Overpass place type: {place_type}")

        query = self._build_query(lat, lng, radius_m, spec.tags)
        try:
            response = requests.post(
                self.OVERPASS_URL,
                data={"data": query},
                timeout=self.timeout,
                headers={"User-Agent": "safesphere-disaster-response/1.0"},
            )
            response.raise_for_status()
            elements = response.json().get("elements", [])
            places = [self._format_place(element, lat, lng, spec) for element in elements]
            places.sort(key=lambda item: item["distance_km"])
            return places[:limit]
        except Exception as exc:
            logger.warning("Overpass nearby search failed for %s: %s", place_type, exc)
            return []

    def search_shelters(self, lat: float, lng: float, limit: int = 5) -> List[Dict[str, Any]]:
        return [self._as_shelter(item) for item in self.search(lat, lng, "shelter", limit=limit)]

    def search_hospitals(self, lat: float, lng: float, limit: int = 5) -> List[Dict[str, Any]]:
        return [self._as_hospital(item) for item in self.search(lat, lng, "hospital", limit=limit)]

    def search_resources(
        self,
        lat: float,
        lng: float,
        category: Optional[str] = None,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        place_types = self._resource_place_types(category)
        results: List[Dict[str, Any]] = []
        per_type_limit = max(limit, 3)
        for place_type in place_types:
            results.extend(self.search(lat, lng, place_type, limit=per_type_limit))
        results.sort(key=lambda item: item["distance_km"])
        return [self._as_resource(item) for item in results[:limit]]

    @staticmethod
    def _build_query(
        lat: float,
        lng: float,
        radius_m: int,
        tags: Tuple[Tuple[str, str], ...],
    ) -> str:
        clauses = []
        for key, value in tags:
            clauses.extend(
                [
                    f'node["{key}"="{value}"](around:{radius_m},{lat},{lng});',
                    f'way["{key}"="{value}"](around:{radius_m},{lat},{lng});',
                    f'relation["{key}"="{value}"](around:{radius_m},{lat},{lng});',
                ]
            )
        return f"[out:json][timeout:25];({''.join(clauses)});out center tags;"

    @staticmethod
    def _resource_place_types(category: Optional[str]) -> List[str]:
        if not category:
            return ["food", "water", "pharmacy", "charging"]
        normalized = category.strip().lower()
        mapping = {
            "food": ["food"],
            "water": ["water"],
            "medicine": ["pharmacy", "hospital"],
            "medical": ["pharmacy", "hospital"],
            "power": ["charging"],
            "charging": ["charging"],
            "fuel": ["charging"],
        }
        return mapping.get(normalized, ["food", "water", "pharmacy", "charging"])

    @staticmethod
    def _format_place(
        element: Dict[str, Any],
        origin_lat: float,
        origin_lng: float,
        spec: OverpassPlaceSpec,
    ) -> Dict[str, Any]:
        tags = element.get("tags") or {}
        lat = element.get("lat") or element.get("center", {}).get("lat")
        lng = element.get("lon") or element.get("center", {}).get("lon")
        name = tags.get("name") or tags.get("operator") or f"OSM {spec.category}"
        address_parts = [
            tags.get("addr:housenumber"),
            tags.get("addr:street"),
            tags.get("addr:suburb"),
            tags.get("addr:city"),
        ]
        address = ", ".join(part for part in address_parts if part) or "OpenStreetMap location"
        return {
            "id": int(element.get("id", 0)),
            "name": name,
            "category": spec.category,
            "quantity": spec.default_quantity,
            "unit": spec.default_unit,
            "location_lat": float(lat),
            "location_lng": float(lng),
            "address": address,
            "contact_number": tags.get("phone") or tags.get("contact:phone"),
            "status": "Available",
            "distance_km": haversine_distance_km(origin_lat, origin_lng, float(lat), float(lng)),
            "source": "overpass",
        }

    @staticmethod
    def _as_shelter(item: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "id": item["id"],
            "name": item["name"],
            "address": item["address"],
            "location_lat": item["location_lat"],
            "location_lng": item["location_lng"],
            "contact_number": item.get("contact_number"),
            "total_beds": 50,
            "available_beds": 20,
            "has_food": True,
            "has_water": True,
            "has_medical": False,
            "has_power": True,
            "distance_km": item["distance_km"],
        }

    @staticmethod
    def _as_hospital(item: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "id": item["id"],
            "name": item["name"],
            "address": item["address"],
            "location_lat": item["location_lat"],
            "location_lng": item["location_lng"],
            "contact_number": item.get("contact_number"),
            "total_beds": 100,
            "available_beds": 30,
            "emergency_services": True,
            "distance_km": item["distance_km"],
        }

    @staticmethod
    def _as_resource(item: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "id": item["id"],
            "name": item["name"],
            "category": item["category"],
            "quantity": item["quantity"],
            "unit": item["unit"],
            "location_lat": item["location_lat"],
            "location_lng": item["location_lng"],
            "address": item["address"],
            "contact_number": item.get("contact_number"),
            "status": item["status"],
            "distance_km": item["distance_km"],
        }


class MapService:
    """Folium map builder for the Streamlit frontend and server-side previews."""

    @staticmethod
    def create_map(
        center_lat: float,
        center_lng: float,
        zoom_start: int = 13,
        tiles: str = "OpenStreetMap",
    ) -> Any:
        try:
            import folium
        except ImportError as exc:
            raise RuntimeError("folium is required for map rendering.") from exc
        return folium.Map(location=[center_lat, center_lng], zoom_start=zoom_start, tiles=tiles)

    @staticmethod
    def add_marker(
        map_obj: Any,
        lat: float,
        lng: float,
        popup: str,
        tooltip: str,
        color: str = "blue",
        icon: str = "info-sign",
    ) -> Any:
        import folium

        folium.Marker(
            location=[lat, lng],
            popup=popup,
            tooltip=tooltip,
            icon=folium.Icon(color=color, icon=icon, prefix="fa"),
        ).add_to(map_obj)
        return map_obj

    @staticmethod
    def add_user_location(map_obj: Any, lat: float, lng: float) -> Any:
        MapService.add_marker(
            map_obj,
            lat,
            lng,
            popup="<b>User location</b>",
            tooltip="User location",
            color="blue",
            icon="user",
        )
        return MapService.add_radius(map_obj, lat, lng, radius_m=500)

    @staticmethod
    def add_radius(map_obj: Any, lat: float, lng: float, radius_m: int) -> Any:
        import folium

        folium.Circle(
            location=[lat, lng],
            radius=radius_m,
            color="#2563eb",
            fill=True,
            fill_opacity=0.08,
        ).add_to(map_obj)
        return map_obj

    @staticmethod
    def add_shelter_locations(map_obj: Any, shelters: List[Dict[str, Any]]) -> Any:
        for shelter in shelters:
            MapService.add_marker(
                map_obj,
                shelter["location_lat"],
                shelter["location_lng"],
                popup=f"<b>{shelter['name']}</b><br>{shelter['address']}",
                tooltip="Emergency shelter",
                color="green",
                icon="home",
            )
        return map_obj

    @staticmethod
    def add_hospital_locations(map_obj: Any, hospitals: List[Dict[str, Any]]) -> Any:
        for hospital in hospitals:
            MapService.add_marker(
                map_obj,
                hospital["location_lat"],
                hospital["location_lng"],
                popup=f"<b>{hospital['name']}</b><br>{hospital['address']}",
                tooltip="Hospital",
                color="cadetblue",
                icon="plus-square",
            )
        return map_obj

    @staticmethod
    def add_disaster_zones(map_obj: Any, incidents: List[Dict[str, Any]]) -> Any:
        import folium

        for incident in incidents:
            lat = incident["location_lat"]
            lng = incident["location_lng"]
            severity = incident.get("severity", "Medium")
            color = "#ef4444" if severity in {"Critical", "High"} else "#f59e0b"
            folium.Circle(
                location=[lat, lng],
                radius=700 if severity in {"Critical", "High"} else 350,
                color=color,
                fill=True,
                fill_opacity=0.12,
            ).add_to(map_obj)
        return map_obj

    @staticmethod
    def add_polygon(
        map_obj: Any,
        coordinates: List[Coordinate],
        popup: str = "Disaster zone",
        color: str = "#ef4444",
    ) -> Any:
        import folium

        folium.Polygon(
            locations=coordinates,
            popup=popup,
            color=color,
            fill=True,
            fill_opacity=0.25,
        ).add_to(map_obj)
        return map_obj

    @staticmethod
    def add_heatmap(map_obj: Any, points: List[Coordinate]) -> Any:
        from folium.plugins import HeatMap

        HeatMap(points, radius=20, blur=15).add_to(map_obj)
        return map_obj

    @staticmethod
    def add_route(map_obj: Any, coordinates: List[Coordinate], color: str = "#2563eb") -> Any:
        import folium

        folium.PolyLine(
            locations=coordinates,
            color=color,
            weight=5,
            opacity=0.85,
            tooltip="Evacuation route",
        ).add_to(map_obj)
        return map_obj


class MapsService:
    """Backward-compatible facade used by existing agent tools."""

    @staticmethod
    def geocode(address: str) -> Dict[str, Any]:
        return GeocodingService().geocode(address)

    @staticmethod
    def reverse_geocode(lat: float, lng: float) -> Dict[str, Any]:
        return GeocodingService().reverse_geocode(lat, lng)

    @staticmethod
    def get_route(
        origin_lat: float,
        origin_lng: float,
        dest_lat: float,
        dest_lng: float,
    ) -> Dict[str, Any]:
        return RoutingService().calculate_route(origin_lat, origin_lng, dest_lat, dest_lng)
