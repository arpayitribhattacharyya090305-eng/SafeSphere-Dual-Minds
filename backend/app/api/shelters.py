from fastapi import APIRouter, Query
from backend.app.tools.agent_tools import get_closest_shelters, get_closest_hospitals
from backend.app.schemas.schemas import ShelterOut, HospitalOut
from typing import List

router = APIRouter(tags=["Relief Centers"])

@router.get("/shelters/nearby", response_model=List[ShelterOut])
def get_nearby_shelters(lat: float = Query(..., description="Latitude"), lng: float = Query(..., description="Longitude"), limit: int = 5):
    return get_closest_shelters(lat, lng, limit)

@router.get("/hospitals/nearby", response_model=List[HospitalOut])
def get_nearby_hospitals(lat: float = Query(..., description="Latitude"), lng: float = Query(..., description="Longitude"), limit: int = 5):
    return get_closest_hospitals(lat, lng, limit)
