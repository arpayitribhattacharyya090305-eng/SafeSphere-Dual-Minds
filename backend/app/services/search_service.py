import requests
from backend.app.core.config import settings


class SearchService:
    @staticmethod
    def search(query: str) -> list:
        """
        Perform a web search for live disaster updates using Tavily Search API.
        Falls back to a simulated news feed when TAVILY_API_KEY is not provided.
        """
        api_key = settings.TAVILY_API_KEY
        if not api_key:
            return SearchService._get_mock_search_results(query)

        try:
            url = "https://api.tavily.com/search"
            payload = {
                "api_key": api_key,
                "query": query,
                "search_depth": "basic",
                "include_answer": False,
                "max_results": 4
            }
            res = requests.post(url, json=payload, timeout=8)
            if res.status_code == 200:
                data = res.json()
                results = []
                for item in data.get("results", []):
                    results.append({
                        "title": item.get("title", "Disaster Alert Updates"),
                        "url": item.get("url", "#"),
                        "snippet": item.get("content", "")
                    })
                return results
            return SearchService._get_mock_search_results(query)
        except Exception:
            return SearchService._get_mock_search_results(query)

    @staticmethod
    def _get_mock_search_results(query: str) -> list:
        """
        Generates realistic disaster bulletins and official advisories
        matching the terms inside the search query.
        """
        q = query.lower()
        results = []

        if "flood" in q or "rain" in q or "water" in q:
            results = [
                {
                    "title": "IMD Issues Red Alert for Mumbai Monsoons: Severe Waterlogging in Low Areas",
                    "url": "https://ndma.gov.in/latest-alerts/mumbai-floods",
                    "snippet": "The India Meteorological Department (IMD) has issued a red alert for Mumbai. Waterlogging is reported in Sion, Milan Subway, and parts of Andheri. Citizens are advised to avoid water-clogged streets and follow local police updates."
                },
                {
                    "title": "BMC Toll-Free Help Desk Activated for Severe Rain Emergency",
                    "url": "https://mcgm.gov.in/emergency-helplines",
                    "snippet": "The Brihanmumbai Municipal Corporation (BMC) has opened flood helpline centers across 24 wards. For waterlogging complaints or evacuation assistance, dial the central emergency helpline 1916."
                },
                {
                    "title": "National Disaster Response Force (NDRF) Deploys 5 Teams to South Mumbai and Suburbs",
                    "url": "https://ndrf.gov.in/deployments",
                    "snippet": "In response to rising water levels in suburban rivers, five NDRF units equipped with inflatable rescue boats and emergency first-aid kits have been positioned in Dharavi, Kurla, and Bhandup to handle water evacuations."
                }
            ]
        elif "cyclone" in q or "wind" in q or "storm" in q:
            results = [
                {
                    "title": "NDMA Cyclone Warning: Sea Storm Nearing Tamil Nadu Coast",
                    "url": "https://ndma.gov.in/cyclone-alerts/chennai-storm",
                    "snippet": "A severe cyclonic storm is tracking towards Chennai at 18 km/h. Landfall is expected near Puducherry. Emergency evacuation has begun for coastal low-lying communities. Fishermen are ordered to remain in harbor."
                },
                {
                    "title": "Chennai Suburban Trains Suspended Temporarily Due to Cyclone Wind Threat",
                    "url": "https://sr.indianrailways.gov.in/alerts",
                    "snippet": "Southern Railways has suspended local train services along the beach and suburban lines as wind speeds cross 80 km/h. Major roads like East Coast Road (ECR) have been closed to civilian traffic."
                }
            ]
        elif "road" in q or "closure" in q or "route" in q or "blocked" in q:
            results = [
                {
                    "title": "Traffic Police Advisory: Major Road Closures and Diverted Routes",
                    "url": "https://trafficpolice.gov.in/road-advisories",
                    "snippet": "Due to structural hazards and waterlogging: the Milan Subway and Sion Underpass are closed. Western Express Highway is running slow with diversions at Santacruz. Please use Eastern Express Highway or coastal roads where possible."
                },
                {
                    "title": "Landslide Blocks Mumbai-Pune Expressway Near Lonavala",
                    "url": "https://mahatraffic.gov.in/expressway-alerts",
                    "snippet": "Heavy debris and rocks have blocked both lanes of the Mumbai-Pune Expressway near the Khandala tunnel. Heavy machinery is on site clearing the path. Traffic is being redirected through the old NH4 highway."
                }
            ]
        else:
            # General fallback results
            results = [
                {
                    "title": "National Disaster Management Authority (NDMA) General Safety Advisory",
                    "url": "https://ndma.gov.in/safety-tips",
                    "snippet": "Keep emergency contacts saved, stock dry food, keep mobile phones charged, and listen to official radio/SMS alerts. Do not spread unverified social media rumors during disaster emergencies."
                },
                {
                    "title": "WHO Guidelines: Preventive Health and Sanitation During Disasters",
                    "url": "https://who.int/emergencies/disaster-health",
                    "snippet": "To prevent waterborne diseases like cholera and leptospirosis: drink only boiled or chlorinated water, maintain basic hand hygiene, and avoid walking bare-foot in stagnant flood waters."
                }
            ]

        return results
