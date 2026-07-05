import requests
from backend.app.core.config import settings


class WeatherService:
    @staticmethod
    def unavailable(reason: str = "Live weather API unavailable") -> dict:
        return {
            "temp": None,
            "feels_like": None,
            "humidity": None,
            "wind_speed": None,
            "description": reason,
            "city": "Live source unavailable",
            "alerts": [],
            "source": "OpenWeather",
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
            return WeatherService.unavailable("OpenWeather API key is not configured")

        try:
            url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
            res = requests.get(url, timeout=8)
            if res.status_code != 200:
                return WeatherService.unavailable(f"OpenWeather current weather returned HTTP {res.status_code}")

            data = res.json()
            alerts = []
            one_call_url = f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&exclude=minutely,hourly&appid={api_key}"
            try:
                alert_res = requests.get(one_call_url, timeout=8)
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
            return WeatherService.unavailable(f"Unable to fetch live OpenWeather data: {exc}")
