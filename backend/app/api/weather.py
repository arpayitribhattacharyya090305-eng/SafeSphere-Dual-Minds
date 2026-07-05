from fastapi import APIRouter, Query
from backend.app.services.weather_service import WeatherService

router = APIRouter(prefix="/weather", tags=["Weather"])

@router.get("/alerts")
def get_weather_alerts(lat: float = Query(..., description="Latitude"), lng: float = Query(..., description="Longitude")):
    return WeatherService.get_weather(lat, lng)
