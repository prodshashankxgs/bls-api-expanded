# FRED Scraper Setup Instructions

This guide will help you set up the FRED scraper system with website mirroring and the `load_data(ticker, date)` interface.

## Prerequisites

- Python 3.8+
- Git
- Terminal/Command Line access

## Installation

### 1. Install Dependencies

```bash
# Install all required packages
pip install -r requirements.txt
```

### 2. Initialize Scrapy Project

```bash
# The scrapy project is already created in the fred_scraper directory
# Verify it's working by checking the spiders
cd fred_scraper
scrapy list
# Should show: fred
cd ..
```

### 3. Test the System

```bash
# Test the main data loader
python fred_data_loader.py
```

## Usage

### Basic Usage

```python
from fred_data_loader import load_data

# Load unemployment data
unemployment = load_data('UNEMPLOYMENT')
if unemployment:
    print(f"Latest unemployment rate: {unemployment.data_points[-1].value}%")

# Load GDP data  
gdp = load_data('GDP')
if gdp:
    print(f"Latest GDP: {gdp.data_points[-1].value} {gdp.units}")

# Load data for specific date
historical_cpi = load_data('CPI', '2023-01-01')
```

### Advanced Usage

```python
from fred_data_loader import FREDDataLoader

# Create loader with custom settings
loader = FREDDataLoader(
    cache_dir="my_cache",
    enable_scraping=True,
    enable_bls_fallback=True
)

# Load data with more options
data = loader.load_data(
    ticker='FEDFUNDS',
    years_back=5,
    force_refresh=True  # Force fresh scrape
)

# Get available tickers
tickers = loader.get_available_tickers()
print(f"Available tickers: {tickers[:10]}")
```

## Available Tickers

The system supports these economic indicators:

### FRED Series
- `GDP` - Gross Domestic Product
- `UNEMPLOYMENT` / `UNRATE` - Unemployment Rate
- `INFLATION` / `CPI` / `CPIAUCSL` - Consumer Price Index
- `FEDFUNDS` / `INTEREST_RATE` - Federal Funds Rate
- `PAYEMS` / `JOBS` / `EMPLOYMENT` - Total Nonfarm Payrolls
- `HOUSING` / `HOUST` - Housing Starts
- `EUR_USD` - Euro to USD Exchange Rate
- `USD_JPY` - USD to Japanese Yen
- `OIL` - Crude Oil Prices
- `GOLD` - Gold Prices
- `SP500` - S&P 500 Index
- `VIX` - Volatility Index

### BLS Series (Fallback)
- `unemployment_bls` - BLS Unemployment Rate
- `inflation_bls` - BLS CPI
- `jobs_bls` - BLS Employment
- `wages` - Average Hourly Earnings
- `productivity` - Labor Productivity

## Data Sources & Fallback System

The system tries data sources in this order:

1. **Cache** (1 hour expiry) - Fastest access
2. **Local Database** - SQLite storage
3. **FRED Scraping** - Real-time data from FRED website
4. **BLS API** - Fallback for BLS-specific indicators

## Scraping Features

### Stealth Capabilities
- **User Agent Rotation** - Multiple realistic browser agents
- **Request Delays** - Intelligent delays to avoid detection
- **Mirror Caching** - Stores pages locally to reduce requests
- **Respectful Scraping** - Follows rate limits and delays

### Mirroring System
- **Automatic Caching** - Pages cached for 24 hours by default
- **Compression** - Gzip compression for efficient storage
- **LRU Eviction** - Removes oldest entries when cache fills
- **Size Management** - 500MB cache limit by default

## Running Scrapy Directly

### Single Series
```bash
cd fred_scraper
scrapy crawl fred -a series_id=GDP
```

### Multiple Series
```bash
cd fred_scraper
scrapy crawl fred  # Scrapes all popular series
```

### With Custom Settings
```bash
cd fred_scraper
scrapy crawl fred -a series_id=UNRATE -s DOWNLOAD_DELAY=3
```

## Configuration

### Cache Settings
Edit `fred_data_loader.py`:
```python
loader = FREDDataLoader(
    cache_dir="custom_cache",        # Cache directory
    db_path="custom_data.db",        # Database path
    enable_scraping=True,            # Enable FRED scraping
    enable_bls_fallback=True         # Enable BLS fallback
)
```

### Scrapy Settings
Edit `fred_scraper/settings.py`:
```python
DOWNLOAD_DELAY = 3               # Delay between requests
CONCURRENT_REQUESTS = 4          # Max concurrent requests
MIRROR_CACHE_EXPIRY = 7200      # Cache expiry in seconds
```

### Mirror Cache Settings
Edit `mirror_system.py`:
```python
cache = MirrorCache(
    cache_dir="mirrors",
    max_age_hours=24,      # Cache expiry
    max_size_mb=500,       # Max cache size
    compress=True          # Enable compression
)
```

## Monitoring

### Cache Statistics
```python
from mirror_system import mirror_cache

stats = mirror_cache.get_cache_stats()
print(f"Cache entries: {stats['total_entries']}")
print(f"Cache size: {stats['total_size_mb']:.1f} MB")
print(f"Utilization: {stats['utilization_percent']:.1f}%")
```

### Log Monitoring
The system logs to Python's logging system. To see detailed logs:

```python
import logging
logging.basicConfig(level=logging.INFO)

# Now all operations will show detailed logs
data = load_data('GDP')
```

## Troubleshooting

### Common Issues

1. **ModuleNotFoundError: scrapy**
   ```bash
   pip install scrapy
   ```

2. **No data returned**
   - Check internet connection
   - Verify ticker name is correct
   - Try with `force_refresh=True`

3. **Scraping blocked**
   - Increase delays in settings
   - Clear mirror cache: `mirror_cache.clear_cache()`
   - Try different user agents

4. **Database locked**
   - Close any other connections to the database
   - Restart the Python process

### Debug Mode
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# This will show all internal operations
loader = FREDDataLoader()
data = loader.load_data('GDP', force_refresh=True)
```

## API Integration

To integrate with your existing FastAPI:

```python
# In app/main.py
from fred_data_loader import load_data

@app.get("/fred/{ticker}")
async def get_fred_data(ticker: str, date: str = None):
    data = load_data(ticker, date)
    if data:
        return {
            "series_id": data.series_id,
            "title": data.title,
            "latest_value": data.data_points[-1].value,
            "latest_date": data.data_points[-1].date,
            "data_points": len(data.data_points),
            "source": data.source
        }
    else:
        raise HTTPException(status_code=404, detail="Data not found")
```

## Performance Tips

1. **Use caching** - Don't disable it unless necessary
2. **Batch requests** - Load multiple tickers together when possible
3. **Monitor delays** - Increase if getting blocked
4. **Regular cleanup** - Occasionally clear old cache data
5. **Use database** - Enable database storage for persistence

## Security Notes

- The scraper respects robots.txt by default (can be disabled)
- Uses realistic user agents and delays
- Rotates requests to appear human-like
- Caches aggressively to minimize server load
- Falls back to official APIs when possible

This system provides real-time economic data while being respectful to the FRED website and avoiding detection issues. 