from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.models.database_models import Volunteer
from backend.app.schemas.schemas import VolunteerRegister, VolunteerOut
from backend.app.tools.agent_tools import match_nearby_volunteers
from typing import List, Optional

router = APIRouter(prefix="/volunteers", tags=["Volunteer System"])

@router.post("/register", response_model=VolunteerOut)
def register_volunteer(volunteer_in: VolunteerRegister, db: Session = Depends(get_db)):
    volunteer = Volunteer(
        name=volunteer_in.name,
        skill_set=volunteer_in.skill_set,
        phone=volunteer_in.phone,
        email=volunteer_in.email,
        status="Available",
        location_lat=volunteer_in.location_lat,
        location_lng=volunteer_in.location_lng,
        address=volunteer_in.address
    )
    db.add(volunteer)
    db.commit()
    db.refresh(volunteer)
    return volunteer

@router.get("/match", response_model=List[VolunteerOut])
def get_matched_volunteers(
    lat: float = Query(..., description="Latitude"),
    lng: float = Query(..., description="Longitude"),
    required_skills: Optional[str] = Query(None, description="Comma separated skill search terms: first-aid, rescue, translation"),
    limit: int = 5
):
    return match_nearby_volunteers(lat, lng, required_skills, limit)
