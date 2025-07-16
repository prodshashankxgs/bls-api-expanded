# app/series_catalog.py
"""
Comprehensive BLS series catalog with focus on CPI and PPI data
"""


class BLSSeriesCatalog:
    """Comprehensive catalog of BLS series with hierarchical organization"""

    def __init__(self):
        self.series_catalog = {
            # ==========================================
            # CONSUMER PRICE INDEX (CPI)
            # ==========================================
            "cpi": {
                "description": "Consumer Price Index - Measures inflation from consumer perspective",
                "base_url": "https://www.bls.gov/cpi/",
                "series": {
                    # CPI-U (All Urban Consumers) - Most Common
                    "cpi_all_items": {
                        "id": "CUUR0000SA0",
                        "title": "CPI-U All Items",
                        "description": "All items, seasonally adjusted",
                        "units": "Index 1982-84=100",
                        "frequency": "Monthly",
                        "seasonal_adjustment": "Seasonally Adjusted"
                    },
                    "cpi_all_items_nsa": {
                        "id": "CUUR0000SA0",
                        "title": "CPI-U All Items (Not Seasonally Adjusted)",
                        "description": "All items, not seasonally adjusted",
                        "units": "Index 1982-84=100",
                        "frequency": "Monthly",
                        "seasonal_adjustment": "Not Seasonally Adjusted"
                    },

                    # Major CPI Categories
                    "cpi_food": {
                        "id": "CUUR0000SAF",
                        "title": "CPI-U Food",
                        "description": "Food and beverages",
                        "units": "Index 1982-84=100"
                    },
                    "cpi_food_home": {
                        "id": "CUUR0000SAF11",
                        "title": "CPI-U Food at Home",
                        "description": "Grocery food",
                        "units": "Index 1982-84=100"
                    },
                    "cpi_food_away": {
                        "id": "CUUR0000SEFV",
                        "title": "CPI-U Food Away from Home",
                        "description": "Restaurant meals",
                        "units": "Index 1982-84=100"
                    },

                    # Energy
                    "cpi_energy": {
                        "id": "CUUR0000SAE",
                        "title": "CPI-U Energy",
                        "description": "All energy commodities",
                        "units": "Index 1982-84=100"
                    },
                    "cpi_gasoline": {
                        "id": "CUUR0000SETB01",
                        "title": "CPI-U Gasoline",
                        "description": "Motor fuel",
                        "units": "Index 1982-84=100"
                    },
                    "cpi_electricity": {
                        "id": "CUUR0000SEHF01",
                        "title": "CPI-U Electricity",
                        "description": "Household electricity",
                        "units": "Index 1982-84=100"
                    },

                    # Housing
                    "cpi_housing": {
                        "id": "CUUR0000SAH",
                        "title": "CPI-U Housing",
                        "description": "All housing costs",
                        "units": "Index 1982-84=100"
                    },
                    "cpi_shelter": {
                        "id": "CUUR0000SAH1",
                        "title": "CPI-U Shelter",
                        "description": "Rent and homeowner costs",
                        "units": "Index 1982-84=100"
                    },
                    "cpi_rent": {
                        "id": "CUUR0000SEHA",
                        "title": "CPI-U Rent of Primary Residence",
                        "description": "Rental costs",
                        "units": "Index 1982-84=100"
                    },

                    # Transportation
                    "cpi_transportation": {
                        "id": "CUUR0000SAT",
                        "title": "CPI-U Transportation",
                        "description": "All transportation costs",
                        "units": "Index 1982-84=100"
                    },
                    "cpi_used_cars": {
                        "id": "CUUR0000SETA02",
                        "title": "CPI-U Used Cars and Trucks",
                        "description": "Pre-owned vehicles",
                        "units": "Index 1982-84=100"
                    },
                    "cpi_new_cars": {
                        "id": "CUUR0000SETA01",
                        "title": "CPI-U New Cars",
                        "description": "New vehicles",
                        "units": "Index 1982-84=100"
                    },

                    # Medical Care
                    "cpi_medical": {
                        "id": "CUUR0000SAM",
                        "title": "CPI-U Medical Care",
                        "description": "Healthcare costs",
                        "units": "Index 1982-84=100"
                    },

                    # Core CPI (excluding food and energy)
                    "cpi_core": {
                        "id": "CUUR0000SA0L1E",
                        "title": "CPI-U Core (Less Food and Energy)",
                        "description": "Core inflation measure",
                        "units": "Index 1982-84=100"
                    },

                    # Regional CPI (Major Metro Areas)
                    "cpi_new_york": {
                        "id": "CUURA101SA0",
                        "title": "CPI-U New York-Newark-Jersey City",
                        "description": "NYC metro area CPI",
                        "units": "Index 1982-84=100"
                    },
                    "cpi_los_angeles": {
                        "id": "CUURA103SA0",
                        "title": "CPI-U Los Angeles-Long Beach-Anaheim",
                        "description": "LA metro area CPI",
                        "units": "Index 1982-84=100"
                    },
                    "cpi_chicago": {
                        "id": "CUURA207SA0",
                        "title": "CPI-U Chicago-Naperville-Elgin",
                        "description": "Chicago metro area CPI",
                        "units": "Index 1982-84=100"
                    }
                }
            },

            # ==========================================
            # PRODUCER PRICE INDEX (PPI)
            # ==========================================
            "ppi": {
                "description": "Producer Price Index - Measures inflation from producer perspective",
                "base_url": "https://www.bls.gov/ppi/",
                "series": {
                    # Final Demand
                    "ppi_final_demand": {
                        "id": "WPUFD49207",
                        "title": "PPI Final Demand",
                        "description": "Final demand goods and services",
                        "units": "Index Nov 2009=100"
                    },
                    "ppi_final_demand_goods": {
                        "id": "WPUFD49104",
                        "title": "PPI Final Demand Goods",
                        "description": "Final demand goods only",
                        "units": "Index Nov 2009=100"
                    },
                    "ppi_final_demand_services": {
                        "id": "WPUFD49203",
                        "title": "PPI Final Demand Services",
                        "description": "Final demand services only",
                        "units": "Index Nov 2009=100"
                    },

                    # Core PPI
                    "ppi_core": {
                        "id": "WPUFD49116",
                        "title": "PPI Final Demand Less Food and Energy",
                        "description": "Core producer inflation",
                        "units": "Index Nov 2009=100"
                    },

                    # Commodity Groups
                    "ppi_food": {
                        "id": "WPUFD49502",
                        "title": "PPI Final Demand Foods",
                        "description": "Food commodities",
                        "units": "Index Nov 2009=100"
                    },
                    "ppi_energy": {
                        "id": "WPUFD49501",
                        "title": "PPI Final Demand Energy",
                        "description": "Energy commodities",
                        "units": "Index Nov 2009=100"
                    },

                    # Industry-Specific PPI
                    "ppi_construction": {
                        "id": "WPUIP23",
                        "title": "PPI Construction",
                        "description": "Construction industry prices",
                        "units": "Index Dec 2005=100"
                    },
                    "ppi_manufacturing": {
                        "id": "WPUIP31",
                        "title": "PPI Manufacturing",
                        "description": "Manufacturing industry prices",
                        "units": "Index Dec 2005=100"
                    },

                    # Intermediate Demand
                    "ppi_intermediate_demand": {
                        "id": "WPUID49",
                        "title": "PPI Intermediate Demand",
                        "description": "Intermediate goods and services",
                        "units": "Index Nov 2009=100"
                    },

                    # Crude Materials
                    "ppi_crude_materials": {
                        "id": "WPUIP1",
                        "title": "PPI Crude Materials",
                        "description": "Raw materials for further processing",
                        "units": "Index 1982=100"
                    }
                }
            },

            # ==========================================
            # EMPLOYMENT INDICATORS
            # ==========================================
            "employment": {
                "description": "Employment and unemployment statistics",
                "series": {
                    "unemployment_rate": {
                        "id": "LNS14000000",
                        "title": "Unemployment Rate",
                        "units": "Percent"
                    },
                    "labor_force_participation": {
                        "id": "LNS11300000",
                        "title": "Labor Force Participation Rate",
                        "units": "Percent"
                    },
                    "nonfarm_payrolls": {
                        "id": "CES0000000001",
                        "title": "Total Nonfarm Payrolls",
                        "units": "Thousands of Persons"
                    },
                    "avg_hourly_earnings": {
                        "id": "CES0500000003",
                        "title": "Average Hourly Earnings - Private Sector",
                        "units": "Dollars per Hour"
                    }
                }
            },

            # ==========================================
            # PRODUCTIVITY
            # ==========================================
            "productivity": {
                "description": "Productivity and costs measures",
                "series": {
                    "nonfarm_productivity": {
                        "id": "PRS85006092",
                        "title": "Nonfarm Business Productivity",
                        "units": "Index 2012=100"
                    },
                    "unit_labor_costs": {
                        "id": "PRS85006112",
                        "title": "Nonfarm Business Unit Labor Costs",
                        "units": "Index 2012=100"
                    }
                }
            }
        }

    def get_all_cpi_series(self) -> dict:
        """Get all CPI series"""
        return self.series_catalog["cpi"]["series"]

    def get_all_ppi_series(self) -> dict:
        """Get all PPI series"""
        return self.series_catalog["ppi"]["series"]

    def get_series_by_category(self, category: str) -> dict:
        """Get all series in a category"""
        return self.series_catalog.get(category, {}).get("series", {})

    def search_series(self, keyword: str) -> dict:
        """Search for series containing keyword"""
        results = {}
        keyword_lower = keyword.lower()

        for category, category_data in self.series_catalog.items():
            if "series" in category_data:
                for series_name, series_info in category_data["series"].items():
                    if (keyword_lower in series_name.lower() or
                            keyword_lower in series_info["title"].lower() or
                            keyword_lower in series_info.get("description", "").lower()):
                        results[series_name] = series_info

        return results

    def get_inflation_basket(self) -> list[str]:
        """Get key series for comprehensive inflation tracking"""
        return [
            "cpi_all_items",  # Headline CPI
            "cpi_core",  # Core CPI
            "cpi_food",  # Food inflation
            "cpi_energy",  # Energy inflation
            "cpi_housing",  # Housing costs
            "cpi_transportation",  # Transportation
            "cpi_medical",  # Healthcare
            "ppi_final_demand",  # Producer prices
            "ppi_core"  # Core PPI
        ]


# Enhanced BLS Client with expanded series support
class EnhancedBLSClient:
    """
    Enhanced BLS client with comprehensive CPI/PPI coverage
    """

    def __init__(self, api_key: [str] = None):
        self.api_key = api_key
        self.catalog = BLSSeriesCatalog()
        self.base_url = "https://api.bls.gov/publicAPI/v2/timeseries/data/"

    async def get_inflation_data(self, series_type: str = "cpi", years: int = 3) -> dict:
        """
        Get comprehensive inflation data

        Args:
            series_type: "cpi", "ppi", or "both"
            years: Number of years of historical data
        """

        inflation_series = []

        if series_type in ["cpi", "both"]:
            cpi_key_series = [
                "cpi_all_items", "cpi_core", "cpi_food",
                "cpi_energy", "cpi_housing"
            ]
            inflation_series.extend(cpi_key_series)

        if series_type in ["ppi", "both"]:
            ppi_key_series = [
                "ppi_final_demand", "ppi_core", "ppi_food", "ppi_energy"
            ]
            inflation_series.extend(ppi_key_series)

        # Fetch all series concurrently
        results = {}
        for series_name in inflation_series:
            try:
                data = await self._fetch_series(series_name, years)
                results[series_name] = data
            except Exception as e:
                print(f"Error fetching {series_name}: {e}")

        return results

    def get_regional_cpi(self, regions: list[str] = None) -> dict:
        """Get CPI data for specific metropolitan areas"""
        if regions is None:
            regions = ["new_york", "los_angeles", "chicago"]

        regional_series = [f"cpi_{region}" for region in regions]
        return self._fetch_multiple_series(regional_series)

    def create_inflation_dashboard(self) -> dict:
        """Create comprehensive inflation monitoring dashboard"""
        key_series = self.catalog.get_inflation_basket()

        dashboard_data = {}
        for series in key_series:
            try:
                data = self._fetch_series(series, years=1)
                if data and data.get("data"):
                    latest = data["data"][0]
                    dashboard_data[series] = {
                        "latest_value": latest["value"],
                        "period": latest["period"],
                        "year": latest["year"],
                        "title": self.catalog.series_catalog[self._get_category(series)]["series"][series]["title"]
                    }
            except Exception as e:
                print(f"Error in dashboard for {series}: {e}")

        return dashboard_data

    def _get_category(self, series_name: str) -> str:
        """Determine which category a series belongs to"""
        for category, data in self.catalog.series_catalog.items():
            if "series" in data and series_name in data["series"]:
                return category
        return "unknown"