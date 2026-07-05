from fastapi import APIRouter, Query
from backend.app.tools.agent_tools import get_closest_resources
from backend.app.schemas.schemas import ResourceOut
from typing import List, Optional

router = APIRouter(prefix="/resources", tags=["Emergency Inventory"])

@router.get("/nearby", response_model=List[ResourceOut])
def get_nearby_resources(
    lat: float = Query(..., description="Latitude"),
    lng: float = Query(..., description="Longitude"),
    category: Optional[str] = Query(None, description="Supply Category: Food, Water, Medicine, Fuel, Power"),
    limit: int = 5
):
    return get_closest_resources(lat, lng, category, limit)
