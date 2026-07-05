import math

import requests
from backend.app.core.config import settings
from backend.app.core.database import SessionLocal
from backend.app.models.database_models import WeatherAlert


class WeatherService:
    @staticmethod
    def _distance_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        radius_km = 6371.0
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lng2 - lng1)
        a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
        return radius_km * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    @staticmethod
    def _nearest_local_profile(lat: float, lon: float) -> dict:
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
        return min(profiles, key=lambda item: WeatherService._distance_km(lat, lon, item["lat"], item["lng"]))

    @staticmethod
    def _local_alerts(city: str) -> list[dict]:
        db = SessionLocal()
        try:
            return [
                {
                    "event": alert.alert_type,
                    "description": alert.description or "",
                    "sender": "Local disaster response database",
                    "severity": alert.severity,
                }
                for alert in db.query(WeatherAlert)
                .filter(WeatherAlert.city.ilike(city))
                .order_by(WeatherAlert.forecast_date.desc())
                .limit(3)
                .all()
            ]
        except Exception:
            return []
        finally:
            db.close()

    @staticmethod
    def unavailable(
        reason: str = "Live weather API unavailable",
        lat: float = 19.0760,
        lon: float = 72.8777,
    ) -> dict:
        profile = WeatherService._nearest_local_profile(lat, lon)
        return {
            "temp": profile["temp"],
            "feels_like": profile["feels_like"],
            "humidity": profile["humidity"],
            "wind_speed": profile["wind_speed"],
            "description": profile["description"],
            "city": profile["city"],
            "alerts": WeatherService._local_alerts(profile["city"]),
            "source": f"Local emergency fallback ({reason})",
            "is_live": False,
        }

    @staticmethod
    def get_weather(lat: float, lon: float) -> dict:
        """
        Fetch real-time weather and active alerts for the given coordinates.
        No simulated weather is returned; when live data is unavailable the
        response explicitly says so and contains empty alerts.
        """
        api_key = settings.OPENWEATHER_API_KEY
        if not api_key:
            return WeatherService.unavailable("OpenWeather API key is not configured", lat, lon)

        try:
            url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
            res = requests.get(url, timeout=2)
            if res.status_code != 200:
                return WeatherService.unavailable(f"OpenWeather current weather returned HTTP {res.status_code}", lat, lon)

            data = res.json()
            alerts = []
            one_call_url = f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&exclude=minutely,hourly&appid={api_key}"
            try:
                alert_res = requests.get(one_call_url, timeout=2)
                if alert_res.status_code == 200:
                    alert_data = alert_res.json()
                    for alert in alert_data.get("alerts", []):
                        event = alert.get("event", "Weather alert")
                        alerts.append({
                            "event": event,
                            "description": alert.get("description", ""),
                            "sender": alert.get("sender_name", "OpenWeather"),
                            "severity": "High" if "severe" in event.lower() else "Medium",
                        })
            except Exception:
                alerts = []

            return {
                "temp": data["main"].get("temp"),
                "feels_like": data["main"].get("feels_like"),
                "humidity": data["main"].get("humidity"),
                "wind_speed": data.get("wind", {}).get("speed"),
                "description": data.get("weather", [{}])[0].get("description", "Live weather").capitalize(),
                "city": data.get("name", "Current location"),
                "alerts": alerts,
                "source": "OpenWeather",
                "is_live": True,
            }
        except Exception as exc:
            return WeatherService.unavailable(f"Unable to fetch live OpenWeather data: {exc}", lat, lon)
