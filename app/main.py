# app/main.py - Enhanced with comprehensive CPI/PPI endpoints

from fastapi import FastAPI, HTTPException, Query, Path
from fastapi.responses import JSONResponse
from typing import List, Dict, Optional
from enum import Enum
from datetime import datetime

from .series_catalog import BLSSeriesCatalog, EnhancedBLSClient
from .models import SeriesResponse, InflationDashboard, RegionalCPIResponse

app = FastAPI(
    title="Comprehensive BLS Data API",
    version="2.0.0",
    description="Full-featured BLS API with comprehensive CPI, PPI, and economic data coverage"
)

# Initialize enhanced components
catalog = BLSSeriesCatalog()
bls_client = EnhancedBLSClient()


class SeriesCategory(str, Enum):
    CPI = "cpi"
    PPI = "ppi"
    EMPLOYMENT = "employment"
    PRODUCTIVITY = "productivity"


class InflationType(str, Enum):
    CPI = "cpi"
    PPI = "ppi"
    BOTH = "both"


# ==========================================
# CORE ENDPOINTS
# ==========================================

@app.get("/")
async def root():
    return {
        "message": "Comprehensive BLS Data API",
        "total_series": sum(len(cat.get("series", {})) for cat in catalog.series_catalog.values()),
        "categories": {
            "cpi": f"{len(catalog.get_all_cpi_series())} series",
            "ppi": f"{len(catalog.get_all_ppi_series())} series",
            "employment": f"{len(catalog.get_series_by_category('employment'))} series",
            "productivity": f"{len(catalog.get_series_by_category('productivity'))} series"
        },
        "key_endpoints": {
            "/inflation/dashboard": "Comprehensive inflation monitoring",
            "/cpi/all": "All CPI series",
            "/ppi/all": "All PPI series",
            "/inflation/compare": "CPI vs PPI comparison",
            "/search/{keyword}": "Search all series"
        }
    }


# ==========================================
# SERIES DISCOVERY ENDPOINTS
# ==========================================

@app.get("/categories")
async def list_categories():
    """List all available data categories"""
    return {
        category: {
            "description": data.get("description", ""),
            "series_count": len(data.get("series", {})),
            "base_url": data.get("base_url", "")
        }
        for category, data in catalog.series_catalog.items()
    }


@app.get("/categories/{category}")
async def get_category_series(category: SeriesCategory):
    """Get all series in a specific category"""
    series = catalog.get_series_by_category(category.value)
    if not series:
        raise HTTPException(status_code=404, detail=f"Category {category} not found")

    return {
        "category": category.value,
        "series_count": len(series),
        "series": series
    }


@app.get("/search/{keyword}")
async def search_series(keyword: str):
    """Search for series by keyword"""
    results = catalog.search_series(keyword)
    return {
        "keyword": keyword,
        "matches": len(results),
        "results": results
    }


# ==========================================
# CPI SPECIFIC ENDPOINTS
# ==========================================

@app.get("/cpi/all")
async def get_all_cpi_series():
    """Get list of all available CPI series"""
    return {
        "category": "Consumer Price Index (CPI)",
        "total_series": len(catalog.get_all_cpi_series()),
        "series": catalog.get_all_cpi_series()
    }


@app.get("/cpi/{series_name}")
async def get_cpi_data(
        series_name: str,
        years: int = Query(default=3, ge=1, le=10),
        enhanced: bool = Query(default=True)
):
    """Get specific CPI series data"""

    cpi_series = catalog.get_all_cpi_series()
    if series_name not in cpi_series:
        available = list(cpi_series.keys())
        raise HTTPException(
            status_code=404,
            detail=f"CPI series '{series_name}' not found. Available: {available[:10]}..."
        )

    # Use your existing get_series_data logic here
    return await get_enhanced_series_data(series_name, years, enhanced)


@app.get("/cpi/categories/food")
async def get_food_cpi():
    """Get all food-related CPI series"""
    food_series = [
        "cpi_food", "cpi_food_home", "cpi_food_away"
    ]

    results = {}
    for series in food_series:
        try:
            data = await get_cpi_data(series, years=2, enhanced=True)
            results[series] = data
        except Exception as e:
            results[series] = {"error": str(e)}

    return {
        "category": "Food CPI",
        "description": "Food and beverage price inflation",
        "data": results
    }


@app.get("/cpi/categories/housing")
async def get_housing_cpi():
    """Get all housing-related CPI series"""
    housing_series = [
        "cpi_housing", "cpi_shelter", "cpi_rent"
    ]

    results = {}
    for series in housing_series:
        try:
            data = await get_cpi_data(series, years=2, enhanced=True)
            results[series] = data
        except Exception as e:
            results[series] = {"error": str(e)}

    return {
        "category": "Housing CPI",
        "description": "Housing and shelter costs",
        "data": results
    }


@app.get("/cpi/regional")
async def get_regional_cpi(
        regions: List[str] = Query(default=["new_york", "los_angeles", "chicago"])
):
    """Get CPI data for specific metropolitan areas"""

    results = {}
    for region in regions:
        series_name = f"cpi_{region}"
        try:
            data = await get_cpi_data(series_name, years=2, enhanced=True)
            results[region] = data
        except Exception as e:
            results[region] = {"error": str(e)}

    return {
        "regional_cpi": results,
        "available_regions": ["new_york", "los_angeles", "chicago"]
    }


# ==========================================
# PPI SPECIFIC ENDPOINTS
# ==========================================

@app.get("/ppi/all")
async def get_all_ppi_series():
    """Get list of all available PPI series"""
    return {
        "category": "Producer Price Index (PPI)",
        "total_series": len(catalog.get_all_ppi_series()),
        "series": catalog.get_all_ppi_series()
    }


@app.get("/ppi/{series_name}")
async def get_ppi_data(
        series_name: str,
        years: int = Query(default=3, ge=1, le=10),
        enhanced: bool = Query(default=True)
):
    """Get specific PPI series data"""

    ppi_series = catalog.get_all_ppi_series()
    if series_name not in ppi_series:
        available = list(ppi_series.keys())
        raise HTTPException(
            status_code=404,
            detail=f"PPI series '{series_name}' not found. Available: {available[:10]}..."
        )

    return await get_enhanced_series_data(series_name, years, enhanced)


@app.get("/ppi/final-demand")
async def get_final_demand_ppi():
    """Get final demand PPI breakdown"""
    final_demand_series = [
        "ppi_final_demand", "ppi_final_demand_goods", "ppi_final_demand_services"
    ]

    results = {}
    for series in final_demand_series:
        try:
            data = await get_ppi_data(series, years=2, enhanced=True)
            results[series] = data
        except Exception as e:
            results[series] = {"error": str(e)}

    return {
        "category": "Final Demand PPI",
        "description": "Producer prices for final demand goods and services",
        "data": results
    }


# ==========================================
# INFLATION ANALYSIS ENDPOINTS
# ==========================================

@app.get("/inflation/dashboard")
async def inflation_dashboard(
        inflation_type: InflationType = Query(default=InflationType.BOTH),
        years: int = Query(default=2, ge=1, le=5)
):
    """Comprehensive inflation monitoring dashboard"""

    try:
        data = await bls_client.get_inflation_data(inflation_type.value, years)

        # Calculate key metrics
        dashboard = {
            "snapshot_date": datetime.now().date().isoformat(),
            "inflation_type": inflation_type.value,
            "key_indicators": {},
            "trends": {},
            "summary": ""
        }

        # Process each series
        for series_name, series_data in data.items():
            if series_data and series_data.get("data"):
                latest = series_data["data"][0]
                dashboard["key_indicators"][series_name] = {
                    "latest_value": latest["value"],
                    "period": latest["period"],
                    "year": latest["year"],
                    "title": series_data.get("title", series_name)
                }

        return dashboard

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating dashboard: {str(e)}")


@app.get("/inflation/compare")
async def compare_inflation_measures(
        years: int = Query(default=3, ge=1, le=5)
):
    """Compare key inflation measures side by side"""

    comparison_series = [
        "cpi_all_items",  # Consumer inflation
        "cpi_core",  # Core consumer inflation
        "ppi_final_demand",  # Producer inflation
        "ppi_core"  # Core producer inflation
    ]

    results = {}
    for series in comparison_series:
        try:
            data = await get_enhanced_series_data(series, years, enhanced=True)
            results[series] = data
        except Exception as e:
            results[series] = {"error": str(e)}

    return {
        "comparison_title": "Key Inflation Measures Comparison",
        "series_data": results,
        "analysis": {
            "consumer_vs_producer": "Compare CPI vs PPI to see inflation pipeline",
            "core_vs_headline": "Core measures exclude volatile food/energy"
        }
    }


@app.get("/inflation/regions")
async def regional_inflation_comparison():
    """Compare inflation across major metropolitan areas"""

    regions = ["new_york", "los_angeles", "chicago"]
    results = {}

    for region in regions:
        try:
            series_name = f"cpi_{region}"
            data = await get_cpi_data(series_name, years=2, enhanced=True)
            results[region] = data
        except Exception as e:
            results[region] = {"error": str(e)}

    return {
        "regional_inflation": results,
        "description": "CPI comparison across major metropolitan areas"
    }


# ==========================================
# HELPER FUNCTIONS
# ==========================================

async def get_enhanced_series_data(series_name: str, years: int, enhanced: bool):
    """Helper function to get enhanced series data (reuse your existing logic)"""
    # This would use your existing data fetching and enhancement logic
    # from the previous implementation
    pass


# ==========================================
# BULK DATA ENDPOINTS
# ==========================================

@app.post("/bulk/inflation")
async def bulk_inflation_data(
        series_list: List[str],
        years: int = Query(default=2, ge=1, le=5)
):
    """Get multiple inflation series in one request"""

    results = {}

    for series_name in series_list:
        try:
            data = await get_enhanced_series_data(series_name, years, enhanced=True)
            results[series_name] = data
        except Exception as e:
            results[series_name] = {"error": str(e)}

    return {
        "bulk_request": {
            "series_count": len(series_list),
            "successful": len([r for r in results.values() if "error" not in r]),
            "failed": len([r for r in results.values() if "error" in r])
        },
        "data": results
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)