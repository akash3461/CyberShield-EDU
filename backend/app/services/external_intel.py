import httpx
from app.config import settings
from app.utils.logger import logger

class ExternalIntelService:
    def __init__(self):
        self.urlscan_api_key = settings.URLSCAN_API_KEY
        self.base_url = "https://urlscan.io/api/v1"

    async def check_url_reputation(self, url: str):
        """Checks URL reputation using urlscan.io API."""
        if not self.urlscan_api_key:
            logger.warning("URLScan API Key not configured. Skipping external check.")
            return None

        headers = {
            "Content-Type": "application/json",
            "API-Key": self.urlscan_api_key
        }
        
        try:
            async with httpx.AsyncClient() as client:
                # Perform a search for existing results first to avoid burning quota
                search_url = f"{self.base_url}/search/?q=url:\"{url}\""
                response = await client.get(search_url, headers=headers, timeout=5.0)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("results"):
                        # Get the most recent result
                        latest = data["results"][0]
                        task_id = latest.get("task", {}).get("uuid")
                        if task_id:
                            # Return verdict if available
                            verdicts = latest.get("verdicts", {})
                            return {
                                "malicious": verdicts.get("overall", {}).get("malicious", False),
                                "score": verdicts.get("overall", {}).get("score", 0),
                                "tags": latest.get("page", {}).get("tags", [])
                            }
                
                return None
        except Exception as e:
            logger.error(f"Error checking external intel for {url}: {str(e)}")
            return None

external_intel = ExternalIntelService()
