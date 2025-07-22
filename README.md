# BLS Economic Data Scraper

Fast, reliable BLS economic data scraper - clone and run locally for easy data access.

## 🚀 Quick Setup (30 seconds)

```bash
# 1. Clone the repo
git clone <your-repo-url>
cd BLS-Scraper-API

# 2. Install dependencies  
pip install -r requirements.txt

# 3. Start the API server
python start.py
# OR manually: python app.py
```

**That's it!** API runs at `http://localhost:5000` in the background.

### ✅ Verify it's working:
```bash
python test_api.py  # Run comprehensive tests
# OR quick check:
curl http://localhost:5000/health
```

## 💻 How to Use in Your Code

### Option 1: Direct API calls (recommended)
```python
import requests

# Get CPI data
response = requests.get('http://localhost:5000/data/cpi?date=2022-2024')
data = response.json()['data']

print(f"Latest CPI: {data[0]['value']} ({data[0]['date']})")
```

### Option 2: Import the module directly
```python
from bls_scraper import load_data

# Load economic data
cpi_data = load_data('cpi', '2022-2024')
unemployment = load_data('unemployment', 'last 3 years')
```

## Available Indicators

- `cpi` - Consumer Price Index All Items
- `cpi_core` - Core CPI (less food/energy)
- `cpi_food` - Food CPI
- `cpi_energy` - Energy CPI  
- `cpi_housing` - Housing CPI
- `ppi` - Producer Price Index
- `unemployment` - Unemployment Rate
- `gdp` - Gross Domestic Product

## Date Formats

- Single year: `'2023'`
- Year range: `'2020-2024'`
- Relative: `'last 5 years'`
- Default: Last 3 years if no date provided

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Command Line

```bash
# Interactive demo
python main.py

# Performance tests
python main.py --test

# Clear cache
python main.py --clear-cache
```

### Python API

```python
from bls_scraper import load_data

# Get CPI data
data = load_data('cpi', '2022-2024')

# Each data point contains:
# - series_id: Official BLS series ID  
# - date: ISO date (YYYY-MM-DD)
# - value: Economic indicator value
# - year: Year
# - month: Month (1-12)
# - category: Human-readable category
# - source: Data source (fred_csv, bls_historical, cache)
```

## Performance

- **Fresh data**: 2-5 seconds
- **Cached data**: <0.1 seconds  
- **Cache duration**: 1 hour
- **Success rate**: >95% with fallback sources

## 📊 Quick API Examples

```bash
# Check if it's running
curl http://localhost:5000/health

# Get available indicators
curl http://localhost:5000/indicators

# Get CPI data for 2022-2024
curl "http://localhost:5000/data/cpi?date=2022-2024"

# Get unemployment data as CSV
curl "http://localhost:5000/data/unemployment?date=2023&format=csv"
```

## 🔧 Troubleshooting

**Port already in use?** Change the port in `app.py`:
```python
# Line 155 in app.py
port = int(os.environ.get('PORT', 5001))  # Change to 5001 or any free port
```

**No data returned?** Check the ticker name:
```bash
curl http://localhost:5000/indicators  # See all available tickers
```

## Files

- `bls_scraper.py` - Core scraping engine
- `app.py` - Flask API server (production-ready)
- `main.py` - Command line interface
- `setup.py` - Package installation
- `requirements.txt` - Dependencies
- `Dockerfile` - Container deployment
- `DEPLOYMENT.md` - Complete deployment guide
- `data_cache/` - Cached data (auto-created)

## Architecture

Production-ready design with:
- Flask REST API server
- Unified scraper class
- Intelligent caching system
- Multiple data sources with fallbacks
- Anti-detection features
- Docker containerization
- Comprehensive error handling & logging