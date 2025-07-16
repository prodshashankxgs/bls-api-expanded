from pydantic import BaseModel
from datetime import date
from typing import List, Optional, Dict, Any


class DataPoint(BaseModel):
    date: date
    value: float
    period: str
    year: int

    # Enhanced fields - these add value over raw BLS data
    month_change: Optional[float] = None
    year_change: Optional[float] = None
    trend: Optional[str] = None


class SeriesResponse(BaseModel):
    series_name: str
    series_id: str
    title: str
    units: str
    data: List[DataPoint]
    last_updated: date
    total_points: int
    fetch_time_seconds: Optional[float] = None
    cached: bool = False


class ComparisonResponse(BaseModel):
    comparison_title: str
    series1: SeriesResponse
    series2: SeriesResponse
    latest_values: Dict[str, float]
    correlation: Optional[float] = None


class DashboardResponse(BaseModel):
    snapshot_date: date
    indicators: Dict[str, Dict[str, Any]]
    summary: str
    total_fetch_time: float


class ErrorResponse(BaseModel):
    error: str
    detail: str
    suggestion: Optional[str] = None


class InflationDashboard(BaseModel):
    snapshot_date: date
    inflation_type: str
    key_indicators: Dict[str, Dict[str, Any]]
    trends: Dict[str, Any]
    summary: str


class RegionalCPIResponse(BaseModel):
    regional_cpi: Dict[str, SeriesResponse]
    available_regions: List[str]