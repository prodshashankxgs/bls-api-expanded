# Standardized Professional Data Schema

## Overview

The BLS Scraper API now includes a **standardized professional data schema** that transforms basic economic data into hedge fund-ready JSON responses. This brings the API up to professional trading system standards similar to Polygon.io, Bloomberg API, and other institutional data providers.

## Format Comparison

### Before: Legacy Format
```json
[
  {
    "series_id": "CPIAUCSL",
    "date": "2024-12-01", 
    "value": 317.603,
    "period": "2024-12",
    "year": 2024,
    "month": 12
  }
]
```

### After: Professional Standardized Format
```json
{
  "success": true,
  "data": [
    {
      "date": "2024-12-01",
      "value": 317.603,
      "period": "2024-12", 
      "year": 2024,
      "month": 12,
      "quarter": null,
      "revision_status": "final"
    }
  ],
  "series": {
    "id": "CPIAUCSL",
    "name": "Consumer Price Index for All Urban Consumers: All Items",
    "description": "Measures the average change in prices of goods and services for urban consumers",
    "category": "inflation",
    "frequency": "monthly",
    "units": "index_1982_84_100",
    "seasonal_adjustment": "seasonally_adjusted",
    "last_updated": "2025-07-17T12:41:35.187007",
    "source_agency": "Bureau of Labor Statistics"
  },
  "metadata": {
    "timestamp": "2025-07-17T12:41:35.187007",
    "source": "cached",
    "quality": "medium",
    "latency_ms": 0,
    "total_points": 12,
    "api_version": "1.0.0",
    "rate_limit_remaining": null,
    "cache_expires": null
  },
  "error": null
}
```

## Key Features

### 1. **Rich Metadata**
- **Timestamp**: ISO format request timestamp
- **Source**: Data source type (cached, live_scraped, fred_csv, etc.)
- **Quality**: Data quality indicator (high/medium/low)
- **Latency**: Response time in milliseconds
- **Total Points**: Number of data points returned
- **API Version**: For backward compatibility

### 2. **Series Information**
- **Official Series ID**: Government series identifier (CPIAUCSL, PPIFIS, etc.)
- **Human-readable Name**: Full descriptive name
- **Description**: Detailed explanation of what the data measures
- **Category**: Economic category (inflation, employment, etc.)
- **Frequency**: Data frequency (monthly, quarterly, annual)
- **Units**: Measurement units (index, percent, etc.)
- **Seasonal Adjustment**: Whether data is seasonally adjusted
- **Source Agency**: Government agency providing the data

### 3. **Enhanced Data Points**
- **Revision Status**: preliminary, revised, final
- **Quarter Support**: For quarterly data series
- **Consistent Date Format**: ISO date format (YYYY-MM-DD)

### 4. **Professional Error Handling**
- **Success Status**: Boolean success indicator
- **Error Messages**: Detailed error descriptions when failures occur
- **Graceful Degradation**: API continues to work even with partial failures

## Data Quality Indicators

| Quality | Description | Sources |
|---------|-------------|---------|
| **HIGH** | Official government APIs | BLS API, FRED API |
| **MEDIUM** | Official CSV downloads, validated cache | FRED CSV, Cached Data |
| **LOW** | Web scraping, single source | HTML scraping |

## Source Types

| Source | Description | Quality | Latency |
|--------|-------------|---------|---------|
| `cached` | Pre-downloaded data files | Medium | ~1ms |
| `live_scraped` | Fresh web scraping | Medium | ~500ms |
| `bls_api` | Official BLS API | High | ~2000ms |
| `fred_api` | Official FRED API | High | ~1000ms |
| `fred_csv` | FRED CSV downloads | Medium | ~500ms |

## Usage Examples

### Backward Compatible (Legacy Format)
```python
from app.fast_bls_api import load_data

# Returns simple list (old format)
data = load_data('cpi', '2024', standardized=False)
print(data[0]['value'])  # 317.603
```

### Professional Format (Recommended)
```python
from app.fast_bls_api import load_data

# Returns standardized professional format
response = load_data('cpi', '2024', standardized=True)

if response['success']:
    # Access metadata
    print(f"Latency: {response['metadata']['latency_ms']}ms")
    print(f"Quality: {response['metadata']['quality']}")
    
    # Access series info
    series = response['series']
    print(f"Series: {series['name']}")
    print(f"Units: {series['units']}")
    
    # Access data
    latest = response['data'][0]
    print(f"Latest CPI: {latest['value']} ({latest['date']})")
    print(f"Status: {latest['revision_status']}")
else:
    print(f"Error: {response['error']}")
```

### Live Scraping with Professional Format
```python
from app.live_bls_scraper import load_data

response = load_data('cpi', '2024', standardized=True)

if response['success']:
    metadata = response['metadata']
    print(f"Fresh data from: {metadata['source']}")
    print(f"Scraped in: {metadata['latency_ms']}ms")
    print(f"Data points: {metadata['total_points']}")
    
    # Data is guaranteed fresh
    for point in response['data'][:3]:
        print(f"{point['date']}: {point['value']}")
```

## Error Handling

### Successful Response
```json
{
  "success": true,
  "data": [...],
  "series": {...},
  "metadata": {...},
  "error": null
}
```

### Error Response
```json
{
  "success": false,
  "data": [],
  "series": {...},
  "metadata": {
    "timestamp": "2025-07-17T12:41:35.187007",
    "source": "live_scraped",
    "quality": "medium",
    "latency_ms": 2500,
    "total_points": 0,
    "api_version": "1.0.0"
  },
  "error": "Failed to scrape cpi: Connection timeout"
}
```

## Hedge Fund Ready Features

### ✅ **Institutional Standards**
- Consistent JSON schema across all endpoints
- Performance monitoring with latency tracking
- Data quality indicators for risk management
- Source attribution for compliance
- API versioning for system stability

### ✅ **Trading System Integration**
- Structured error handling for automated systems
- Metadata for caching and refresh strategies
- Quality indicators for data validation
- Timestamp tracking for audit trails

### ✅ **Professional Documentation**
- Complete series descriptions and metadata
- Units and measurement specifications
- Data frequency and update schedules
- Source agency attribution

## Migration Guide

### Updating Existing Code
```python
# Old way (still works)
data = load_data('cpi', '2024')
latest_value = data[0]['value']

# New way (recommended)
response = load_data('cpi', '2024', standardized=True)
if response['success']:
    latest_value = response['data'][0]['value']
    data_quality = response['metadata']['quality']
    latency = response['metadata']['latency_ms']
```

### Gradual Migration
1. **Phase 1**: Add `standardized=True` to new code
2. **Phase 2**: Update critical paths to use standardized format
3. **Phase 3**: Migrate all code to standardized format
4. **Phase 4**: Remove legacy format support (optional)

## Performance Impact

| Format | Response Size | Parse Time | Benefits |
|--------|---------------|------------|----------|
| **Legacy** | ~200 bytes | ~0.1ms | Simple, fast |
| **Standardized** | ~800 bytes | ~0.3ms | Rich metadata, professional |

**Recommendation**: Use standardized format for production systems, legacy format for simple scripts.

## API Versioning

The standardized schema includes API versioning to ensure backward compatibility:

- **v1.0.0**: Initial standardized schema
- **v1.1.0**: Added revision status and quarterly data support
- **v2.0.0**: Future breaking changes (if needed)

Version is included in every response for tracking and compatibility.

---

## Summary

The standardized schema transforms the BLS API from a simple data scraper into a **professional economic data service** suitable for hedge funds and trading systems. It maintains 100% backward compatibility while adding enterprise-grade features expected by institutional users. 