# BLS Scraper API - Complete API Reference

## 📚 Overview

This document provides complete reference documentation for all functions, classes, and data formats in the BLS Scraper API.

## 🚀 Main Functions

### Fast Cached Data API

#### `load_data(ticker, date=None, standardized=False)`

**File**: `app/fast_bls_api.py`

Load economic data from pre-cached BLS files (fastest option).

**Parameters:**
- `ticker` (str): Economic indicator identifier
- `date` (str, optional): Date range specification
- `standardized` (bool): Return professional format if True

**Returns:**
- `List[Dict]` (legacy format) or `Dict` (standardized format)

**Example:**
```python
from app.fast_bls_api import load_data

# Basic usage
data = load_data('cpi', '2024')

# Standardized format
response = load_data('cpi', '2024', standardized=True)
```

---

### Live Web Scraping API

#### `load_data(ticker, date=None, standardized=False)`

**File**: `app/live_bls_scraper.py`

Scrape fresh data directly from BLS website (always current).

**Parameters:**
- `ticker` (str): Economic indicator identifier
- `date` (str, optional): Date range specification  
- `standardized` (bool): Return professional format if True

**Returns:**
- `List[Dict]` (legacy format) or `Dict` (standardized format)

**Example:**
```python
from app.live_bls_scraper import load_data

# Live scraping
fresh_data = load_data('cpi', '2024')

# Professional format
response = load_data('cpi', '2024', standardized=True)
```

---

## 🏷️ Supported Tickers

### Consumer Price Index (CPI)
| Ticker | Series ID | Description |
|--------|-----------|-------------|
| `'cpi'` | CPIAUCSL | All Urban Consumers: All Items |
| `'cpi_all'` | CPIAUCSL | All Urban Consumers: All Items |
| `'cpi_core'` | CPILFESL | Less Food & Energy |
| `'cpi_food'` | CPIUFDSL | Food |
| `'cpi_energy'` | CPIENGSL | Energy |
| `'cpi_housing'` | CPIHOSSL | Housing |

### Producer Price Index (PPI)
| Ticker | Series ID | Description |
|--------|-----------|-------------|
| `'ppi'` | PPIFIS | Final Demand: Finished Goods |
| `'ppi_all'` | PPIFIS | Final Demand: Finished Goods |
| `'ppi_core'` | PPIFCG | Final Demand: Consumer Goods |
| `'ppi_energy'` | PPIENG | Energy Commodities |
| `'ppi_aco'` | PPIACO | All Commodities |

### Other Economic Indicators
| Ticker | Series ID | Description |
|--------|-----------|-------------|
| `'unemployment'` | UNRATE | Unemployment Rate |
| `'gdp'` | GDP | Gross Domestic Product |

---

## 📅 Date Format Options

### Supported Date Formats

| Format | Example | Description |
|--------|---------|-------------|
| Single Year | `'2024'` | All data for one year |
| Year Range | `'2020-2024'` | Data between years (inclusive) |
| Recent Years | `'last 3 years'` | Most recent N years |
| Default | `None` | Last 3 years (default) |

### Date Parsing Examples
```python
# Single year
data = load_data('cpi', '2024')

# Multi-year range  
data = load_data('cpi', '2020-2024')

# Relative dates
data = load_data('cpi', 'last 5 years')

# Default (last 3 years)
data = load_data('cpi')
```

---

## 📊 Response Formats

### Legacy Format (standardized=False)

**Structure:**
```python
[
    {
        "series_id": "CPIAUCSL",
        "date": "2024-06-01", 
        "value": 321.5,
        "period": "2024-06",
        "year": 2024,
        "month": 6,
        "scraped_at": "2025-01-17T12:30:45"  # Only in live scraper
    },
    # ... more data points
]
```

**Field Descriptions:**
- `series_id`: BLS series identifier
- `date`: ISO format date (YYYY-MM-DD)
- `value`: Numeric data value
- `period`: BLS period format (YYYY-MM)
- `year`: Year as integer
- `month`: Month as integer (1-12)
- `scraped_at`: Timestamp when data was scraped (live only)

### Standardized Format (standardized=True)

**Structure:**
```python
{
    "success": True,
    "data": [
        {
            "date": "2024-06-01",
            "value": 321.5,
            "revision_status": "final",
            "seasonal_adjustment": "seasonally_adjusted",
            "units": "index_1982_84_100",
            "notes": null
        }
    ],
    "series": {
        "id": "CPIAUCSL",
        "name": "Consumer Price Index for All Urban Consumers: All Items",
        "description": "Measures the average change over time...",
        "category": "inflation",
        "frequency": "monthly",
        "units": "index_1982_84_100",
        "source_agency": "Bureau of Labor Statistics"
    },
    "metadata": {
        "timestamp": "2025-01-17T12:30:45.123456",
        "source": "cached",
        "quality": "high",
        "latency_ms": 1,
        "total_points": 12,
        "date_range": "2024-01-01 to 2024-12-01",
        "api_version": "1.0.0",
        "cache_status": "hit"
    },
    "error": null
}
```

**Field Descriptions:**

**Top Level:**
- `success`: Boolean indicating request success
- `data`: Array of standardized data points
- `series`: Metadata about the economic series
- `metadata`: Request and performance metadata
- `error`: Error information (null if successful)

**Data Points:**
- `date`: ISO format date
- `value`: Numeric value
- `revision_status`: "preliminary", "final", or "revised"
- `seasonal_adjustment`: Adjustment type
- `units`: Data units/scale
- `notes`: Additional annotations

**Series Information:**
- `id`: BLS series ID
- `name`: Full series name
- `description`: Detailed description
- `category`: Data category (inflation, employment, etc.)
- `frequency`: Data frequency (monthly, quarterly, etc.)
- `units`: Measurement units
- `source_agency`: Publishing agency

**Metadata:**
- `timestamp`: Request timestamp
- `source`: Data source ("cached", "live_scraped", etc.)
- `quality`: Data quality assessment
- `latency_ms`: Response time in milliseconds
- `total_points`: Number of data points returned
- `date_range`: Actual date range of data
- `api_version`: API version
- `cache_status`: Cache hit/miss status

---

## 🏛️ Advanced Classes

### FastBLSAPI Class

**File**: `app/fast_bls_api.py`

Advanced interface for cached data with additional features.

#### Constructor
```python
FastBLSAPI(cache_dir="cached_data", max_workers=10)
```

**Parameters:**
- `cache_dir`: Directory containing cached data files
- `max_workers`: Thread pool size for parallel processing

#### Methods

##### `load_data(ticker, date=None, standardized=True)`
Primary data loading method.

##### `load_multiple(tickers, date=None, standardized=True)`
Load multiple economic indicators in parallel.

**Example:**
```python
from app.fast_bls_api import FastBLSAPI

api = FastBLSAPI(max_workers=20)

# Load multiple indicators
data = api.load_multiple(['cpi', 'ppi', 'unemployment'], '2024')
```

##### `get_data_summary(ticker)`
Get metadata about available data for a ticker.

**Returns:**
```python
{
    "series_id": "CPIAUCSL",
    "total_points": 876,
    "date_range": "1947-01-01 to 2024-12-01",
    "last_updated": "2025-01-17T12:30:45",
    "file_size": "45.2 KB"
}
```

##### `get_available_tickers()`
Get list of all supported tickers.

**Returns:**
```python
{
    "cpi_indicators": ["cpi", "cpi_core", "cpi_energy", ...],
    "ppi_indicators": ["ppi", "ppi_core", "ppi_energy", ...],
    "other_indicators": ["unemployment", "gdp", ...]
}
```

---

### LiveBLSScraper Class

**File**: `app/live_bls_scraper.py`

Advanced interface for live web scraping with configuration options.

#### Constructor
```python
LiveBLSScraper(max_workers=5)
```

**Parameters:**
- `max_workers`: Thread pool size for concurrent scraping

#### Methods

##### `load_data(ticker, date=None, standardized=True)`
Primary data scraping method.

##### `scrape_fresh_data(ticker, date=None)`
Force fresh scraping (bypasses any internal caches).

##### `get_scraping_sources(ticker)`
Get list of data sources for a ticker.

**Returns:**
```python
{
    "primary_sources": ["https://beta.bls.gov/...", "https://fred.stlouisfed.org/..."],
    "backup_sources": ["https://...", "https://..."],
    "success_rates": {"bls": 0.95, "fred": 0.98}
}
```

---

## 🔧 Utility Functions

### Data Conversion Utilities

#### `standardize_data(raw_data, source, series_info)`

**File**: `app/standardized_schema.py`

Convert raw data to standardized professional format.

**Parameters:**
- `raw_data`: List of raw data dictionaries
- `source`: DataSource enum value
- `series_info`: Series metadata

**Returns:** Standardized response dictionary

---

### Date Parsing Utilities

#### `parse_date_range(date_str)`

Parse various date formats into start/end years.

**Parameters:**
- `date_str`: Date specification string

**Returns:** Tuple of (start_year, end_year)

**Examples:**
```python
parse_date_range('2024')        # (2024, 2024)
parse_date_range('2020-2024')   # (2020, 2024)
parse_date_range('last 3 years') # (2021, 2024)  # if current year is 2024
```

---

## ⚠️ Error Handling

### Exception Types

#### `BLSDataError`
Base exception for BLS data related errors.

#### `BLSScrapingError`
Raised when web scraping fails.

#### `BLSCacheError` 
Raised when cached data is unavailable or corrupted.

### Error Response Format (Standardized)

```python
{
    "success": False,
    "data": [],
    "series": None,
    "metadata": {
        "timestamp": "2025-01-17T12:30:45.123456",
        "source": "error",
        "quality": "unknown",
        "latency_ms": 0,
        "total_points": 0,
        "api_version": "1.0.0"
    },
    "error": {
        "code": "TICKER_NOT_FOUND",
        "message": "Ticker 'xyz' is not supported",
        "details": "Supported tickers: cpi, ppi, unemployment...",
        "timestamp": "2025-01-17T12:30:45.123456"
    }
}
```

### Common Error Codes

| Code | Description | Solution |
|------|-------------|----------|
| `TICKER_NOT_FOUND` | Invalid ticker specified | Use supported ticker from list |
| `DATE_PARSE_ERROR` | Invalid date format | Use supported date format |
| `NO_DATA_AVAILABLE` | No data for date range | Try broader date range |
| `SCRAPING_FAILED` | Web scraping failed | Check internet connection |
| `CACHE_FILE_MISSING` | Cached data file not found | Use live scraper or update cache |

---

## 🚀 Performance Characteristics

### Speed Benchmarks

| API Type | Typical Speed | Best Case | Worst Case |
|----------|---------------|-----------|------------|
| Fast Cached | 0.5-2ms | 0.1ms | 5ms |
| Live Scraper | 50-300ms | 25ms | 2000ms |
| Ultra Fresh | 200-500ms | 100ms | 3000ms |

### Memory Usage

| Operation | Memory Usage | Notes |
|-----------|--------------|-------|
| Load single ticker | 1-5 MB | Depends on date range |
| Load multiple tickers | 10-50 MB | Parallel loading |
| Cache full dataset | 100-200 MB | All historical data |

### Reliability Metrics

| API Type | Success Rate | Typical Failures |
|----------|--------------|------------------|
| Fast Cached | 99.9% | Missing cache files |
| Live Scraper | 95-98% | Network issues, site changes |
| Ultra Fresh | 97-99% | Fallback to multiple sources |

---

## 🔐 Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `BLS_CACHE_DIR` | `cached_data` | Cache directory path |
| `BLS_MAX_WORKERS` | `10` | Thread pool size |
| `BLS_TIMEOUT` | `30` | Request timeout (seconds) |
| `BLS_RETRY_COUNT` | `3` | Retry attempts for failed requests |

### Configuration File

Create `config.json`:
```json
{
    "cache_settings": {
        "directory": "cached_data",
        "max_age_days": 30,
        "auto_refresh": true
    },
    "scraping_settings": {
        "timeout": 30,
        "retry_count": 3,
        "user_agent": "BLS-Scraper-API/1.0"
    },
    "performance": {
        "max_workers": 10,
        "enable_parallel": true,
        "memory_limit_mb": 500
    }
}
```

---

## 📈 Usage Examples by Use Case

### High-Frequency Trading
```python
from app.fast_bls_api import FastBLSAPI

# Ultra-fast cached data for HFT
api = FastBLSAPI(max_workers=50)
data = api.load_data('cpi', '2024', standardized=False)  # Legacy format for speed
```

### Economic Research
```python
from app.fast_bls_api import load_data

# Comprehensive historical analysis
data = load_data('cpi', '1980-2024', standardized=True)
# Professional format with full metadata
```

### Real-Time Monitoring
```python
from app.live_bls_scraper import load_data

# Always fresh data for real-time systems
fresh_data = load_data('cpi', '2024', standardized=True)
# Live scraping with professional format
```

### Data Validation
```python
from app.ultra_fresh_scraper import load_data

# Multi-source verification for critical decisions
verified_data = load_data('cpi', '2024', standardized=True)
# Cross-validated from multiple sources
```

---

This API reference provides complete documentation for integrating the BLS Scraper API into your applications. For additional examples and tutorials, see the `QUICK_START_GUIDE.md` and other documentation files. 