from __future__ import annotations

import math
from datetime import datetime
from typing import Optional

from backend.app.core.database import Base, SessionLocal, engine
from backend.app.models.database_models import GovernmentScheme, Hospital, Incident, Resource, Shelter, Volunteer, WeatherAlert
from backend.app.rag.kb_docs import DOCUMENTS
from backend.app.seed import seed_database


_DB_READY = False


def _ensure_local_database() -> None:
    global _DB_READY
    if _DB_READY:
        return
    Base.metadata.create_all(bind=engine)
    seed_database()
    _DB_READY = True


def _distance_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    radius_km = 6371.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lng2 - lng1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return round(radius_km * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)), 2)


def local_shelters(lat: float, lng: float, limit: int = 6) -> list[dict]:
    _ensure_local_database()
    db = SessionLocal()
    try:
        items = []
        for shelter in db.query(Shelter).all():
            items.append(
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
                    "distance_km": _distance_km(lat, lng, shelter.location_lat, shelter.location_lng),
                }
            )
        return sorted(items, key=lambda item: item["distance_km"])[:limit]
    finally:
        db.close()


def local_hospitals(lat: float, lng: float, limit: int = 6) -> list[dict]:
    _ensure_local_database()
    db = SessionLocal()
    try:
        items = []
        for hospital in db.query(Hospital).all():
            items.append(
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
                    "distance_km": _distance_km(lat, lng, hospital.location_lat, hospital.location_lng),
                }
            )
        return sorted(items, key=lambda item: item["distance_km"])[:limit]
    finally:
        db.close()


def local_resources(
    lat: float,
    lng: float,
    category: Optional[str] = None,
    limit: int = 5,
) -> list[dict]:
    _ensure_local_database()
    db = SessionLocal()
    try:
        query = db.query(Resource)
        if category and category != "All":
            query = query.filter(Resource.category.ilike(category))

        items = []
        for resource in query.all():
            items.append(
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
                    "distance_km": _distance_km(lat, lng, resource.location_lat, resource.location_lng),
                }
            )
        return sorted(items, key=lambda item: item["distance_km"])[:limit]
    finally:
        db.close()


def local_incidents() -> list[dict]:
    _ensure_local_database()
    db = SessionLocal()
    try:
        incidents = [
            {
                "id": incident.id,
                "reporter_id": incident.reporter_id,
                "title": incident.title,
                "description": incident.description,
                "location_lat": incident.location_lat,
                "location_lng": incident.location_lng,
                "address": incident.address,
                "disaster_type": incident.disaster_type,
                "severity": incident.severity,
                "status": incident.status,
                "image_url": incident.image_url,
                "assessment_details": incident.assessment_details,
                "created_at": incident.created_at,
            }
            for incident in db.query(Incident).order_by(Incident.created_at.desc()).all()
        ]
        if incidents:
            return incidents
    finally:
        db.close()

    return [
        {
            "id": 1,
            "reporter_id": None,
            "title": "Waterlogging near low-lying road",
            "description": "Heavy rainfall has created waterlogging near an underpass. Avoid the route and use higher roads.",
            "location_lat": 19.0760,
            "location_lng": 72.8777,
            "address": "Mumbai",
            "disaster_type": "Flood",
            "severity": "Medium",
            "status": "Monitoring",
            "image_url": None,
            "assessment_details": None,
            "created_at": datetime.utcnow(),
        },
        {
            "id": 2,
            "reporter_id": None,
            "title": "Power line hazard reported",
            "description": "Possible loose electric wire reported after strong winds. Keep distance and alert local response teams.",
            "location_lat": 19.0820,
            "location_lng": 72.8840,
            "address": "Mumbai East",
            "disaster_type": "Other",
            "severity": "High",
            "status": "Reported",
            "image_url": None,
            "assessment_details": None,
            "created_at": datetime.utcnow(),
        },
    ]


def add_local_incident(payload: dict) -> bool:
    _ensure_local_database()
    db = SessionLocal()
    try:
        incident = Incident(
            reporter_id=None,
            title=payload["title"],
            description=payload.get("description"),
            location_lat=payload["location_lat"],
            location_lng=payload["location_lng"],
            address=payload.get("address"),
            disaster_type=payload["disaster_type"],
            severity=payload.get("severity", "Medium"),
            status="Reported",
            image_url=payload.get("image_url"),
            assessment_details=payload.get("assessment_details"),
        )
        db.add(incident)
        db.commit()
        return True
    except Exception:
        db.rollback()
        return False
    finally:
        db.close()


def local_volunteers(lat: float, lng: float, required_skills: Optional[str] = None, limit: int = 6) -> list[dict]:
    _ensure_local_database()
    db = SessionLocal()
    try:
        volunteers = db.query(Volunteer).filter(Volunteer.status == "Available").all()
        skill_terms = [
            item.strip().lower()
            for item in (required_skills or "").split(",")
            if item.strip()
        ]
        results = []
        for volunteer in volunteers:
            volunteer_skills = (volunteer.skill_set or "").lower()
            if skill_terms and not any(term in volunteer_skills for term in skill_terms):
                continue
            distance = (
                _distance_km(lat, lng, volunteer.location_lat, volunteer.location_lng)
                if volunteer.location_lat is not None and volunteer.location_lng is not None
                else 999.0
            )
            results.append(
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
                    "distance_km": distance,
                }
            )
        return sorted(results, key=lambda item: item["distance_km"])[:limit]
    finally:
        db.close()


def add_local_volunteer(payload: dict) -> bool:
    _ensure_local_database()
    db = SessionLocal()
    try:
        volunteer = Volunteer(
            name=payload["name"],
            skill_set=payload.get("skill_set"),
            phone=payload["phone"],
            email=payload.get("email"),
            status="Available",
            location_lat=payload.get("location_lat"),
            location_lng=payload.get("location_lng"),
            address=payload.get("address"),
        )
        db.add(volunteer)
        db.commit()
        return True
    except Exception:
        db.rollback()
        return False
    finally:
        db.close()


def local_medical_guidelines(query: str, limit: int = 2) -> list[dict]:
    terms = {term.strip().lower() for term in query.split() if term.strip()}
    aliases = {
        "snakebite": "snake",
        "snake": "snakebite",
        "burn": "burns",
        "panic": "mentalhealth",
        "relief": "mentalhealth",
        "fracture": "fractures",
        "poison": "poisoning",
    }
    expanded_terms = set(terms)
    for term in terms:
        if term in aliases:
            expanded_terms.add(aliases[term])

    scored = []
    for doc in DOCUMENTS:
        haystack = f"{doc['title']} {doc['category']} {doc['content']}".lower()
        score = sum(1 for term in expanded_terms if term in haystack)
        if score:
            scored.append((score, doc))

    if not scored:
        scored = [(1, doc) for doc in DOCUMENTS if doc["category"] == "Medical"]

    scored.sort(key=lambda item: item[0], reverse=True)
    return [doc for _, doc in scored[:limit]]


def local_chat_response(query: str, location: str = "Mumbai") -> dict:
    query_lower = query.lower()
    parts = [
        "### Emergency Action Plan",
        f"- Location: {location}",
        "- Call local emergency services if there is immediate danger.",
        "- Move people away from floodwater, damaged structures, exposed wiring, smoke, or fast traffic.",
        "- Keep phone battery, identity documents, medicines, drinking water, and cash together in a small go-bag.",
    ]
    if "flood" in query_lower or "rain" in query_lower:
        parts.extend(
            [
                "- Move to higher ground and avoid underpasses or waterlogged roads.",
                "- Do not walk or drive through moving water.",
                "- Switch off electricity only if it is safe and dry to reach the main switch.",
            ]
        )
    if "asthma" in query_lower or "breath" in query_lower:
        parts.extend(
            [
                "- Keep the person sitting upright and away from smoke, dust, and cold air.",
                "- Use the prescribed inhaler if available and seek medical help if breathing does not improve.",
            ]
        )
    return {
        "final_response": "\n".join(parts),
        "agent_logs": [
            {
                "agent": "Local Fallback",
                "timestamp": datetime.utcnow().strftime("%H:%M:%S"),
                "action": "Generated offline emergency guidance",
                "status": "Success",
                "findings": "Backend was unavailable, so a local response was prepared.",
            }
        ],
    }


def local_government_schemes(category: Optional[str] = None) -> list[dict]:
    _ensure_local_database()
    db = SessionLocal()
    try:
        query = db.query(GovernmentScheme)
        if category and category != "All":
            query = query.filter(GovernmentScheme.category.ilike(category))

        schemes = [
            {
                "id": scheme.id,
                "title": scheme.title,
                "description": scheme.description,
                "category": scheme.category,
                "eligibility_criteria": scheme.eligibility_criteria,
                "benefit_amount": scheme.benefit_amount,
                "contact_helpline": scheme.contact_helpline,
                "documents_required": scheme.documents_required or [],
            }
            for scheme in query.all()
        ]
        if schemes:
            return schemes
    finally:
        db.close()

    fallback_schemes = [
        {
            "id": 1,
            "title": "NDRF Ex-Gratia Relief Compensation",
            "description": "Financial compensation for families affected by notified natural disasters, including loss of life, injury, crop damage, and severe property damage.",
            "category": "Compensation",
            "eligibility_criteria": "Resident of a declared disaster-affected region with verified loss, injury, or structural damage.",
            "benefit_amount": "Rs. 4,000,000 for loss of life; Rs. 250,000 for permanent disability; Rs. 95,100 for severe house damage.",
            "contact_helpline": "1070 / 1078 (NDMA Helpline)",
            "documents_required": [
                "Disaster Damage Certificate",
                "Aadhaar Card",
                "Bank Account Details",
                "Death Certificate or Medical Report, if applicable",
            ],
        },
        {
            "id": 2,
            "title": "PM National Relief Fund Medical Aid",
            "description": "Medical assistance for disaster-affected citizens undergoing hospital treatment for serious injuries.",
            "category": "Medical Aid",
            "eligibility_criteria": "Disaster victims receiving treatment in a government or empaneled hospital.",
            "benefit_amount": "Up to Rs. 200,000 direct hospital cost coverage.",
            "contact_helpline": "011-23014020 (PMO Relief Wing)",
            "documents_required": [
                "Aadhaar Card",
                "Hospital Admission Slip",
                "Estimated Treatment Cost Bill",
                "Disaster Victim Card or Ration Card",
            ],
        },
        {
            "id": 3,
            "title": "SDRF House Reconstruction Subsidy",
            "description": "State Disaster Response Fund housing grant for rebuilding fully or partly damaged homes.",
            "category": "Housing",
            "eligibility_criteria": "Owner of a residential property damaged by flood, cyclone, landslide, or earthquake, verified by local revenue officials.",
            "benefit_amount": "Rs. 95,100 in hilly areas; Rs. 70,000 in plains; Rs. 15,000 for partial damage.",
            "contact_helpline": "108 (State Disaster Helpline)",
            "documents_required": [
                "Land Ownership Documents",
                "Geotagged Photo of Damaged House",
                "Aadhaar Card",
                "Verification Form signed by Tehsildar",
            ],
        },
    ]
    if category and category != "All":
        return [scheme for scheme in fallback_schemes if scheme["category"].lower() == category.lower()]
    return fallback_schemes


def _nearest_weather_profile(lat: float, lng: float) -> dict:
    profiles = [
        {
            "city": "Mumbai",
            "lat": 19.0760,
            "lng": 72.8777,
            "temp": 29.0,
            "feels_like": 34.0,
            "humidity": 84,
            "wind_speed": 6.2,
            "description": "Heavy rain risk",
        },
        {
            "city": "Chennai",
            "lat": 13.0827,
            "lng": 80.2707,
            "temp": 31.0,
            "feels_like": 37.0,
            "humidity": 78,
            "wind_speed": 8.7,
            "description": "Cyclone watch",
        },
    ]
    return min(profiles, key=lambda item: _distance_km(lat, lng, item["lat"], item["lng"]))


def local_weather(lat: float = 19.0760, lng: float = 72.8777) -> dict:
    _ensure_local_database()
    profile = _nearest_weather_profile(lat, lng)
    db = SessionLocal()
    try:
        alerts = [
            {
                "event": alert.alert_type,
                "description": alert.description,
                "sender": "Local disaster response database",
                "severity": alert.severity,
            }
            for alert in db.query(WeatherAlert)
            .filter(WeatherAlert.city.ilike(profile["city"]))
            .order_by(WeatherAlert.forecast_date.desc())
            .limit(3)
            .all()
        ]
        return {
            "temp": profile["temp"],
            "feels_like": profile["feels_like"],
            "humidity": profile["humidity"],
            "wind_speed": profile["wind_speed"],
            "description": profile["description"],
            "city": profile["city"],
            "alerts": alerts,
            "source": "Local emergency fallback",
            "is_live": False,
        }
    finally:
        db.close()
