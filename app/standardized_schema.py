"""
Standardized JSON Schema for Professional Economic Data API

This module defines the standard data structures and schemas for economic data
that meet professional hedge fund and trading system requirements.
"""

from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Union, Any
from datetime import datetime
from enum import Enum
import json

class DataSource(Enum):
    """Data source types"""
    CACHED = "cached"
    LIVE_SCRAPED = "live_scraped"
    BLS_API = "bls_api"
    FRED_API = "fred_api"
    FRED_CSV = "fred_csv"

class DataQuality(Enum):
    """Data quality indicators"""
    HIGH = "high"      # Official source, validated
    MEDIUM = "medium"  # Scraped, cross-verified
    LOW = "low"        # Scraped, single source

class SeriesType(Enum):
    """Economic data series types"""
    CPI = "consumer_price_index"
    PPI = "producer_price_index"
    UNEMPLOYMENT = "unemployment_rate"
    GDP = "gross_domestic_product"
    INTEREST_RATE = "interest_rate"
    INFLATION = "inflation_rate"

@dataclass
class Metadata:
    """Metadata for API responses"""
    timestamp: str              # ISO format timestamp
    source: str                 # Data source (cached, live_scraped, etc.)
    quality: str                # Data quality indicator
    latency_ms: int            # Response time in milliseconds
    total_points: int          # Number of data points returned
    api_version: str           # API version
    rate_limit_remaining: Optional[int] = None
    cache_expires: Optional[str] = None

@dataclass
class SeriesInfo:
    """Information about the economic data series"""
    id: str                    # Official series ID (e.g., CPIAUCSL)
    name: str                  # Human-readable name
    description: str           # Detailed description
    category: str              # Category (CPI, PPI, etc.)
    frequency: str             # Data frequency (monthly, quarterly, etc.)
    units: str                 # Units of measurement
    seasonal_adjustment: str   # Seasonally adjusted or not
    last_updated: str          # When series was last updated
    source_agency: str         # Source agency (BLS, FRED, etc.)

@dataclass
class DataPoint:
    """Individual economic data point"""
    date: str                  # ISO date format (YYYY-MM-DD)
    value: float               # The economic value
    period: str                # Period identifier (e.g., 2024-12)
    year: int                  # Year
    month: Optional[int] = None        # Month (1-12)
    quarter: Optional[int] = None      # Quarter (1-4) for quarterly data
    revision_status: Optional[str] = None  # preliminary, revised, final
    
@dataclass
class StandardizedResponse:
    """Complete standardized API response"""
    success: bool
    data: List[DataPoint]
    series: SeriesInfo
    metadata: Metadata
    error: Optional[str] = None

class StandardizedDataFormatter:
    """Formats raw data into standardized schema"""
    
    # Series metadata mapping
    SERIES_METADATA = {
        'CPIAUCSL': {
            'name': 'Consumer Price Index for All Urban Consumers: All Items',
            'description': 'Measures the average change in prices of goods and services for urban consumers',
            'category': 'inflation',
            'frequency': 'monthly',
            'units': 'index_1982_84_100',
            'seasonal_adjustment': 'seasonally_adjusted',
            'source_agency': 'Bureau of Labor Statistics'
        },
        'CPILFESL': {
            'name': 'Consumer Price Index for All Urban Consumers: All Items Less Food and Energy',
            'description': 'Core CPI excluding volatile food and energy prices',
            'category': 'inflation',
            'frequency': 'monthly',
            'units': 'index_1982_84_100',
            'seasonal_adjustment': 'seasonally_adjusted',
            'source_agency': 'Bureau of Labor Statistics'
        },
        'PPIFIS': {
            'name': 'Producer Price Index by Industry: Total Manufacturing Industries',
            'description': 'Measures average change in selling prices received by domestic producers',
            'category': 'inflation',
            'frequency': 'monthly',
            'units': 'index_dec_2009_100',
            'seasonal_adjustment': 'seasonally_adjusted',
            'source_agency': 'Bureau of Labor Statistics'
        },
        'UNRATE': {
            'name': 'Unemployment Rate',
            'description': 'Percentage of labor force that is unemployed',
            'category': 'employment',
            'frequency': 'monthly',
            'units': 'percent',
            'seasonal_adjustment': 'seasonally_adjusted',
            'source_agency': 'Bureau of Labor Statistics'
        }
    }
    
    def __init__(self, api_version: str = "1.0.0"):
        self.api_version = api_version
    
    def format_response(
        self,
        raw_data: List[Dict],
        series_id: str,
        source: DataSource,
        start_time: float,
        error: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Convert raw data into standardized response format
        
        Args:
            raw_data: Raw data points from API
            series_id: Economic series identifier
            source: Data source type
            start_time: Request start time for latency calculation
            error: Error message if any
            
        Returns:
            Standardized response dictionary
        """
        latency_ms = int((datetime.now().timestamp() - start_time) * 1000)
        
        # Create metadata
        metadata = Metadata(
            timestamp=datetime.now().isoformat(),
            source=source.value,
            quality=self._determine_quality(source).value,
            latency_ms=latency_ms,
            total_points=len(raw_data) if raw_data else 0,
            api_version=self.api_version
        )
        
        # Create series info
        series_info = self._create_series_info(series_id)
        
        # Convert data points
        data_points = []
        if raw_data and not error:
            for item in raw_data:
                data_point = DataPoint(
                    date=item.get('date', ''),
                    value=float(item.get('value', 0)),
                    period=item.get('period', ''),
                    year=int(item.get('year', 0)),
                    month=item.get('month'),
                    revision_status='final'  # Default for historical data
                )
                data_points.append(data_point)
        
        # Create response
        response = StandardizedResponse(
            success=error is None,
            data=data_points,
            series=series_info,
            metadata=metadata,
            error=error
        )
        
        return asdict(response)
    
    def _determine_quality(self, source: DataSource) -> DataQuality:
        """Determine data quality based on source"""
        quality_map = {
            DataSource.BLS_API: DataQuality.HIGH,
            DataSource.FRED_API: DataQuality.HIGH,
            DataSource.FRED_CSV: DataQuality.MEDIUM,
            DataSource.CACHED: DataQuality.MEDIUM,
            DataSource.LIVE_SCRAPED: DataQuality.MEDIUM
        }
        return quality_map.get(source, DataQuality.LOW)
    
    def _create_series_info(self, series_id: str) -> SeriesInfo:
        """Create series information object"""
        metadata = self.SERIES_METADATA.get(series_id, {
            'name': f'Economic Series {series_id}',
            'description': 'Economic data series',
            'category': 'economic',
            'frequency': 'monthly',
            'units': 'unknown',
            'seasonal_adjustment': 'unknown',
            'source_agency': 'Various'
        })
        
        return SeriesInfo(
            id=series_id,
            name=metadata['name'],
            description=metadata['description'],
            category=metadata['category'],
            frequency=metadata['frequency'],
            units=metadata['units'],
            seasonal_adjustment=metadata['seasonal_adjustment'],
            last_updated=datetime.now().isoformat(),
            source_agency=metadata['source_agency']
        )

# Convenience function for formatting
def standardize_data(
    raw_data: List[Dict],
    series_id: str,
    source: DataSource,
    start_time: float,
    error: Optional[str] = None
) -> Dict[str, Any]:
    """
    Quick function to standardize data using default formatter
    """
    formatter = StandardizedDataFormatter()
    return formatter.format_response(raw_data, series_id, source, start_time, error) 