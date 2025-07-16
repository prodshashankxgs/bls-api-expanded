from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import os
import time
from datetime import date, datetime, timedelta
from typing import Dict
from functools import lru_cache

from .bls_client import BLSClient
from .models import SeriesResponse, DataPoint, ComparisonResponse, ErrorResponse

# Load environment variables
load_dotenv()

app = FastAPI(
    title="BLS Data MVP",
    version="0.1.0",
    description="Enhanced BLS economic data API with friendly names and calculated insights"
)

# Initialize BLS client
bls_client = BLSClient()

# Simple in-memory cache
cache = {}
cache_timestamps = {}
CACHE_TTL = 3600  # 1 hour


def is_cache_valid(key: str) -> bool:
    if key not in cache_timestamps:
        return False
    return datetime.now() - cache_timestamps[key] < timedelta(seconds=CACHE_TTL)


async def cached_bls_request(series_name: str, years: int):
    cache_key = f"{series_name}:{years}"

    if cache_key in cache and is_cache_valid(cache_key):
        data = cache[cache_key]
        data["_cached"] = True
        return data

    # Fetch from BLS
    start_time = datetime.now()
    data = await bls_client.get_series_data(series_name, years)
    fetch_time = (datetime.now() - start_time).total_seconds()

    # Cache the result
    cache[cache_key] = data
    cache_timestamps[cache_key] = datetime.now()

    # Add timing info
    data["_fetch_time"] = fetch_time
    data["_cached"] = False

    return data


@app.get("/")
async def root():
    return {
        "message": "BLS MVP API Ready",
        "features": [
            "Friendly series names (unemployment, inflation, jobs, wages, productivity)",
            "Enhanced calculations (month-over-month, year-over-year changes)",
            "Multi-series comparisons",
            "Economic dashboard",
            "Performance optimizations with caching"
        ],
        "endpoints": {
            "GET /data/{series_name}": "Get enhanced series data",
            "GET /compare": "Compare two series side-by-side",
            "GET /dashboard": "Economic snapshot with key indicators",
            "GET /series": "List all available series"
        },
        "example_usage": [
            "Try: /data/unemployment",
            "Try: /compare?series1=unemployment&series2=inflation",
            "Try: /dashboard"
        ]
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "api_key_configured": bool(os.getenv("BLS_API_KEY") and os.getenv("BLS_API_KEY") != "your_bls_api_key_here"),
        "available_series": len(bls_client.list_available_series()),
        "cache_entries": len(cache)
    }


@app.get("/series")
async def list_series():
    """List all available series with descriptions"""
    return {
        "available_series": bls_client.list_available_series(),
        "total_count": len(bls_client.list_available_series()),
        "usage": "Use series names like 'unemployment', 'inflation', 'jobs' in /data/{series_name}"
    }


def enhance_data_points(data_points: list) -> list:
    """Add calculated fields that provide value over raw BLS data"""

    enhanced_points = []

    for i, point in enumerate(data_points):
        enhanced_point = DataPoint(**point.dict())

        # Month-over-month change
        if i > 0:
            prev_value = data_points[i - 1].value
            if prev_value != 0:
                enhanced_point.month_change = ((point.value - prev_value) / prev_value) * 100

        # Year-over-year change (12 months ago)
        if i >= 12:
            year_ago_value = data_points[i - 12].value
            if year_ago_value != 0:
                enhanced_point.year_change = ((point.value - year_ago_value) / year_ago_value) * 100

        # Simple trend analysis
        if enhanced_point.month_change is not None:
            if enhanced_point.month_change > 0.1:
                enhanced_point.trend = "increasing"
            elif enhanced_point.month_change < -0.1:
                enhanced_point.trend = "decreasing"
            else:
                enhanced_point.trend = "stable"

        enhanced_points.append(enhanced_point)

    return enhanced_points


@app.get("/data/{series_name}", response_model=SeriesResponse)
async def get_series_data(
        series_name: str,
        years: int = Query(default=3, ge=1, le=10, description="Number of years of data to retrieve"),
        enhanced: bool = Query(default=True, description="Include calculated fields (changes, trends)")
):
    """
    Get enhanced data for a specific economic series

    Available series: unemployment, inflation, jobs, wages, productivity
    """

    try:
        start_time = time.time()

        # Get raw data from BLS (with caching)
        raw_data = await cached_bls_request(series_name, years)

        # Convert to our data models
        data_points = []
        for item in raw_data["data"]:
            try:
                parsed_date = bls_client.parse_bls_date(item["year"], item["period"])
                dp = DataPoint(
                    date=parsed_date,
                    value=float(item["value"]),
                    period=item["period"],
                    year=int(item["year"])
                )
                data_points.append(dp)
            except (ValueError, KeyError) as e:
                # Skip invalid data points
                continue

        # Sort by date (newest first for BLS data)
        data_points.sort(key=lambda x: x.date, reverse=True)

        # Add enhancements if requested
        if enhanced and len(data_points) > 1:
            # Reverse for calculations (oldest first), then reverse back
            data_points.reverse()
            data_points = enhance_data_points(data_points)
            data_points.reverse()  # Back to newest first

        fetch_time = time.time() - start_time

        return SeriesResponse(
            series_name=series_name,
            series_id=raw_data["seriesID"],
            title=raw_data.get("friendly_title", raw_data.get("title", "")),
            units=raw_data.get("friendly_units", raw_data.get("units", "")),
            data=data_points,
            last_updated=date.today(),
            total_points=len(data_points),
            fetch_time_seconds=round(fetch_time, 3),
            cached=raw_data.get("_cached", False)
        )

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving data: {str(e)}")


@app.get("/compare", response_model=ComparisonResponse)
async def compare_series(
        series1: str = Query(default="unemployment", description="First series to compare"),
        series2: str = Query(default="inflation", description="Second series to compare"),
        years: int = Query(default=2, ge=1, le=5, description="Years of data for comparison")
):
    """
    Compare two economic series side by side with correlation analysis
    """

    try:
        # Get both series
        data1 = await get_series_data(series1, years, enhanced=True)
        data2 = await get_series_data(series2, years, enhanced=True)

        # Extract latest values
        latest_values = {}
        if data1.data:
            latest_values[series1] = data1.data[0].value  # Newest first
        if data2.data:
            latest_values[series2] = data2.data[0].value

        return ComparisonResponse(
            comparison_title=f"{data1.title} vs {data2.title}",
            series1=data1,
            series2=data2,
            latest_values=latest_values,
            correlation=None  # Could calculate this later
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error comparing series: {str(e)}")


@app.get("/dashboard")
async def economic_dashboard():
    """Get key economic indicators in one call"""

    try:
        start_time = time.time()

        # Get latest data for key indicators
        indicators = {}
        key_series = ["unemployment", "inflation", "jobs", "wages"]

        for series_name in key_series:
            try:
                data = await get_series_data(series_name, years=1, enhanced=True)
                if data.data:
                    latest = data.data[0]  # Most recent data point
                    indicators[series_name] = {
                        "value": latest.value,
                        "date": latest.date.isoformat(),
                        "units": data.units,
                        "title": data.title,
                        "month_change": latest.month_change,
                        "trend": latest.trend
                    }
            except Exception as e:
                indicators[series_name] = {"error": str(e)}

        total_time = time.time() - start_time

        # Create summary
        summary_parts = []
        if "unemployment" in indicators and "value" in indicators["unemployment"]:
            unemployment_rate = indicators["unemployment"]["value"]
            summary_parts.append(f"Unemployment: {unemployment_rate}%")

        if "inflation" in indicators and "value" in indicators["inflation"]:
            # For CPI, we'd need to calculate inflation rate from index
            summary_parts.append("CPI data available")

        dashboard = {
            "snapshot_date": date.today().isoformat(),
            "indicators": indicators,
            "summary": " | ".join(summary_parts) if summary_parts else "Economic data snapshot",
            "total_fetch_time": round(total_time, 3),
            "data_sources": "Bureau of Labor Statistics"
        }

        return dashboard

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating dashboard: {str(e)}")


@app.get("/cache/status")
async def cache_status():
    """Get cache status information"""
    return {
        "cache_entries": len(cache),
        "cache_keys": list(cache.keys()),
        "cache_ttl_seconds": CACHE_TTL,
        "oldest_entry": min(cache_timestamps.values()).isoformat() if cache_timestamps else None,
        "newest_entry": max(cache_timestamps.values()).isoformat() if cache_timestamps else None
    }


@app.delete("/cache/clear")
async def clear_cache():
    """Clear all cached data"""
    global cache, cache_timestamps
    entries_cleared = len(cache)
    cache.clear()
    cache_timestamps.clear()

    return {
        "message": f"Cache cleared successfully",
        "entries_cleared": entries_cleared
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global error handler"""
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal Server Error",
            detail=str(exc),
            suggestion="Check your request parameters and try again. If the error persists, the BLS API might be temporarily unavailable."
        ).dict()
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)