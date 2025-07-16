import httpx
from datetime import datetime, date
from typing import List, Dict, Optional
import os


class BLSClient:
    def __init__(self):
        self.base_url = "https://api.bls.gov/publicAPI/v2/timeseries/data/"
        self.api_key = os.getenv("BLS_API_KEY")

        # MVP: Core economic indicators with friendly names
        self.series_map = {
            "unemployment": {
                "id": "LNS14000000",
                "title": "Unemployment Rate",
                "units": "Percent"
            },
            "inflation": {
                "id": "CUUR0000SA0",
                "title": "Consumer Price Index - All Urban Consumers",
                "units": "Index 1982-84=100"
            },
            "jobs": {
                "id": "CES0000000001",
                "title": "Total Nonfarm Employment",
                "units": "Thousands of Persons"
            },
            "wages": {
                "id": "CES0500000003",
                "title": "Average Hourly Earnings - Private Sector",
                "units": "Dollars per Hour"
            },
            "productivity": {
                "id": "PRS85006092",
                "title": "Nonfarm Business Sector Productivity",
                "units": "Index 2012=100"
            }
        }

    async def get_series_data(self, series_name: str, years: int = 3) -> Dict:
        """Get data for a series from BLS API"""

        if series_name not in self.series_map:
            raise ValueError(f"Unknown series: {series_name}. Available: {list(self.series_map.keys())}")

        series_info = self.series_map[series_name]
        series_id = series_info["id"]

        start_year = datetime.now().year - years
        end_year = datetime.now().year

        payload = {
            "seriesid": [series_id],
            "startyear": str(start_year),
            "endyear": str(end_year)
        }

        # Add API key if available
        if self.api_key and self.api_key != "your_bls_api_key_here":
            payload["registrationkey"] = self.api_key

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(self.base_url, json=payload)
                response.raise_for_status()

                data = response.json()

                if data["status"] != "REQUEST_SUCCEEDED":
                    error_msg = data.get("message", ["Unknown error"])[0]
                    raise Exception(f"BLS API Error: {error_msg}")

                # Enhance the response with our metadata
                series_data = data["Results"]["series"][0]
                series_data["series_name"] = series_name
                series_data["friendly_title"] = series_info["title"]
                series_data["friendly_units"] = series_info["units"]

                return series_data

        except httpx.RequestError as e:
            raise Exception(f"Network error connecting to BLS API: {str(e)}")
        except httpx.HTTPStatusError as e:
            raise Exception(f"BLS API returned error {e.response.status_code}: {e.response.text}")

    def parse_bls_date(self, year: str, period: str) -> date:
        """Convert BLS period notation to actual date"""
        year_int = int(year)

        # Handle monthly data (M01, M02, etc.)
        if period.startswith("M"):
            month = int(period[1:])
            return date(year_int, month, 1)

        # Handle quarterly data (Q01, Q02, etc.)
        elif period.startswith("Q"):
            quarter = int(period[1:])
            month = (quarter - 1) * 3 + 1
            return date(year_int, month, 1)

        # Handle annual data (A01)
        elif period == "A01":
            return date(year_int, 1, 1)

        # Default fallback
        else:
            return date(year_int, 1, 1)

    def list_available_series(self) -> Dict[str, Dict[str, str]]:
        """List all available series with descriptions"""
        return {
            name: {
                "title": info["title"],
                "units": info["units"],
                "bls_series_id": info["id"]
            }
            for name, info in self.series_map.items()
        }

    def get_series_info(self, series_name: str) -> Optional[Dict]:
        """Get information about a specific series"""
        return self.series_map.get(series_name)