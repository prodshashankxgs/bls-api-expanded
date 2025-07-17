# Simple BLS Data API

A Python API for quickly loading BLS (Bureau of Labor Statistics) economic data like CPI and PPI with just one function call: `load_data(ticker, date)`.

## Quick Start

### Installation
```bash
git clone <this-repo>
cd "BLS Scraper API"
pip install -r requirements.txt
```

### Simple Usage
```python
from app.fast_bls_api import load_data

# Get CPI data for 2020-2023
cpi_data = load_data('cpi', '2020-2023')
print(f"Latest CPI: {cpi_data[0]['value']} ({cpi_data[0]['date']})")
```

## Two Data Sources Available

### Option 1: Fast Cached Data (Recommended)
**File**: `app/fast_bls_api.py`  
**Speed**: Milliseconds  
**Data**: Uses pre-cached BLS data from `cached_data/` folder  

```python
from app.fast_bls_api import load_data

# Lightning fast - uses cached data
data = load_data('cpi', '2023-2024')
# Returns data in ~1ms
```

### Option 2: Live Web Scraping 
**File**: `app/live_bls_scraper.py`  
**Speed**: 1-3 seconds  
**Data**: Scrapes fresh data from BLS websites every time  

```python
from app.live_bls_scraper import load_data

# Live scraping - always fresh data
data = load_data('cpi', '2023-2024') 
# Takes 1-3 seconds, scrapes BLS website
```

## Available Data

### Supported Tickers
- `'cpi'` - Consumer Price Index (All Urban Consumers)
- `'cpi_core'` - Core CPI (less food & energy)
- `'cpi_energy'` - Energy prices
- `'cpi_housing'` - Housing prices
- `'ppi'` - Producer Price Index (All Manufacturing)
- `'ppi_core'` - Core PPI
- `'unemployment'` - Unemployment Rate

### Date Formats
- `'2023'` - Single year
- `'2020-2023'` - Year range  
- `'last 3 years'` - Recent years
- `None` - Default (last 3 years)

## Example Usage

```python
#!/usr/bin/env python3

# Option 1: Fast cached data
from app.fast_bls_api import load_data as load_cached

# Option 2: Live web scraping  
from app.live_bls_scraper import load_data as load_live

def main():
    print("=== Fast Cached Data ===")
    cpi_cached = load_cached('cpi', '2023-2024')
    if cpi_cached:
        print(f"CPI: {cpi_cached[0]['value']} ({cpi_cached[0]['date']})")
        print(f"Found {len(cpi_cached)} data points")
    
    print("\n=== Live Web Scraping ===")
    cpi_live = load_live('cpi', '2024')
    if cpi_live:
        print(f"Fresh CPI: {cpi_live[0]['value']} ({cpi_live[0]['date']})")
        print(f"Scraped at: {cpi_live[0]['scraped_at']}")

if __name__ == "__main__":
    main()
```

## Data Structure

Both APIs return the same format:
```python
[
    {
        'series_id': 'CPIAUCSL',
        'date': '2024-12-01',
        'value': 317.603,
        'period': '2024-12',
        'year': 2024,
        'month': 12,
        'scraped_at': '2025-01-17T...'  # Only in live scraper
    },
    # ... more data points
]
```

## Performance Comparison

| Method | Speed | Data Freshness | Use Case |
|--------|--------|----------------|----------|
| **Cached** | ~1ms | Historical + some recent | Fast analysis, backtesting |
| **Live** | 1-3s | Always fresh | Current market data, real-time |

## Testing

Run the included test files:

```bash
# Test cached data API
python final_test.py

# Test live scraping API  
python app/live_bls_scraper.py

# Run demo
python simple_demo.py
```

## Files Structure

```
BLS Scraper API/
├── app/
│   ├── fast_bls_api.py      # Fast cached data API
│   └── live_bls_scraper.py  # Live web scraping API
├── cached_data/             # Pre-cached BLS data files
├── requirements.txt         # Python dependencies
├── final_test.py           # Performance test
├── simple_demo.py          # Usage examples
└── SIMPLE_API_USAGE.md     # Detailed usage guide
```

## When to Use Which

### Use Cached Data API when:
- ✅ You need fast response times (milliseconds)
- ✅ You're doing historical analysis or backtesting
- ✅ You're running many queries frequently
- ✅ You don't need the absolute latest data

### Use Live Scraping API when:
- ✅ You need the most current data available
- ✅ You're building real-time applications
- ✅ You don't mind waiting 1-3 seconds per query
- ✅ You want to ensure no dependency on cached files

## Requirements

- Python 3.7+
- requests
- beautifulsoup4
- lxml

## Notes

- **No BLS API Key Required**: Both options work without BLS API registration
- **No Rate Limits**: The cached version has no rate limits
- **Multiple Formats**: Supports various date input formats
- **Error Handling**: Graceful handling of missing data or network issues
- **Clean Data**: Automatically filters and validates data points

## Troubleshooting

### Live Scraper Returns No Data
- BLS website structure may have changed
- Check internet connection
- Try the cached data API instead

### Cached Data is Old
- Update the `cached_data/` folder with fresh data
- Or use the live scraping API for current data

That's it! Simple as `load_data(ticker, date)` 🚀