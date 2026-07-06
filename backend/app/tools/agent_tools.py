"""Tool functions used by SafeSphere agents."""

from __future__ import annotations

import math
from typing import Optional

from sqlalchemy.orm import Session

from backend.app.core.database import SessionLocal
from backend.app.models.database_models import GovernmentScheme, Hospital, Resource, Shelter, Volunteer
from backend.app.services.maps_service import RoutingService
from backend.app.services.rag_service import RAGService
from backend.app.services.search_service import SearchService
from backend.app.services.weather_service import WeatherService


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Compute direct distance in kilometers using the haversine formula."""
    earth_radius_km = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(earth_radius_km * c, 2)


def get_weather_data(lat: float, lng: float) -> dict:
    return WeatherService.get_weather(lat, lng)


def search_live_news(query: str) -> list:
    return SearchService.search(query)


def calculate_evacuation_route(origin_lat: float, origin_lng: float, dest_lat: float, dest_lng: float) -> dict:
    return RoutingService().calculate_route(origin_lat, origin_lng, dest_lat, dest_lng)


def get_closest_shelters(lat: float, lng: float, limit: int = 3) -> list:
    """Return nearby shelters from the seeded local emergency database."""
    db: Session = SessionLocal()
    try:
        shelters = db.query(Shelter).all()
        scored_shelters = []
        for shelter in shelters:
            dist = calculate_distance(lat, lng, shelter.location_lat, shelter.location_lng)
            scored_shelters.append(
                {
                    "id": shelter.id,
                    "name": shelter.name,
                    "address": shelter.address,
                    "location_lat": shelter.location_lat,
                    "location_lng": shelter.location_lng,
                    "contact_number": shelter.contact_number,
                    "total_beds": shelter.total_beds,
                    "available_beds": shelter.available_beds,
                    "has_food": shelter.has_food,
                    "has_water": shelter.has_water,
                    "has_medical": shelter.has_medical,
                    "has_power": shelter.has_power,
                    "distance_km": dist,
                    "source": "Local seeded database",
                }
            )
        scored_shelters.sort(key=lambda item: item["distance_km"])
        return scored_shelters[:limit]
    finally:
        db.close()


def get_closest_hospitals(lat: float, lng: float, limit: int = 3) -> list:
    """Return nearby hospitals from the seeded local emergency database."""
    db: Session = SessionLocal()
    try:
        hospitals = db.query(Hospital).all()
        scored_hospitals = []
        for hospital in hospitals:
            dist = calculate_distance(lat, lng, hospital.location_lat, hospital.location_lng)
            scored_hospitals.append(
                {
                    "id": hospital.id,
                    "name": hospital.name,
                    "address": hospital.address,
                    "location_lat": hospital.location_lat,
                    "location_lng": hospital.location_lng,
                    "contact_number": hospital.contact_number,
                    "total_beds": hospital.total_beds,
                    "available_beds": hospital.available_beds,
                    "emergency_services": hospital.emergency_services,
                    "distance_km": dist,
                    "source": "Local seeded database",
                }
            )
        scored_hospitals.sort(key=lambda item: item["distance_km"])
        return scored_hospitals[:limit]
    finally:
        db.close()


def get_closest_resources(lat: float, lng: float, category: Optional[str] = None, limit: int = 5) -> list:
    """Return nearby resources from the seeded local emergency database."""
    db: Session = SessionLocal()
    try:
        query = db.query(Resource)
        if category:
            query = query.filter(Resource.category.ilike(category))
        resources = query.all()
        scored_resources = []
        for resource in resources:
            dist = calculate_distance(lat, lng, resource.location_lat, resource.location_lng)
            scored_resources.append(
                {
                    "id": resource.id,
                    "name": resource.name,
                    "category": resource.category,
                    "quantity": resource.quantity,
                    "unit": resource.unit,
                    "location_lat": resource.location_lat,
                    "location_lng": resource.location_lng,
                    "address": resource.address,
                    "contact_number": resource.contact_number,
                    "status": resource.status,
                    "distance_km": dist,
                    "source": "Local seeded database",
                }
            )
        scored_resources.sort(key=lambda item: item["distance_km"])
        return scored_resources[:limit]
    finally:
        db.close()


def query_medical_guidelines(query: str, limit: int = 2) -> list:
    return RAGService.query(query, limit)


def get_gov_schemes(category: Optional[str] = None) -> list:
    db: Session = SessionLocal()
    try:
        query = db.query(GovernmentScheme)
        if category:
            query = query.filter(GovernmentScheme.category.ilike(category))
        schemes = query.all()
        return [
            {
                "id": scheme.id,
                "title": scheme.title,
                "description": scheme.description,
                "category": scheme.category,
                "eligibility_criteria": scheme.eligibility_criteria,
                "benefit_amount": scheme.benefit_amount,
                "contact_helpline": scheme.contact_helpline,
                "documents_required": scheme.documents_required,
            }
            for scheme in schemes
        ]
    finally:
        db.close()


def match_nearby_volunteers(
    lat: float,
    lng: float,
    required_skills: Optional[str] = None,
    limit: int = 3,
) -> list:
    db: Session = SessionLocal()
    try:
        query = db.query(Volunteer).filter(Volunteer.status == "Available")
        volunteers = query.all()
        matched = []
        skills_set = set(skill.strip().lower() for skill in required_skills.split(",")) if required_skills else set()

        for volunteer in volunteers:
            dist = (
                calculate_distance(lat, lng, volunteer.location_lat, volunteer.location_lng)
                if volunteer.location_lat and volunteer.location_lng
                else 999.0
            )
            volunteer_skills = (
                set(skill.strip().lower() for skill in volunteer.skill_set.split(","))
                if volunteer.skill_set
                else set()
            )
            skill_match_count = len(skills_set.intersection(volunteer_skills)) if skills_set else 1

            if not skills_set or skill_match_count > 0:
                matched.append(
                    {
                        "id": volunteer.id,
                        "name": volunteer.name,
                        "skill_set": volunteer.skill_set,
                        "phone": volunteer.phone,
                        "email": volunteer.email,
                        "status": volunteer.status,
                        "location_lat": volunteer.location_lat,
                        "location_lng": volunteer.location_lng,
                        "address": volunteer.address,
                        "distance_km": dist,
                        "match_score": skill_match_count,
                    }
                )

        matched.sort(key=lambda item: (item["distance_km"], -item["match_score"]))
        return matched[:limit]
    finally:
        db.close()
