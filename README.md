# BLS Economic Data Scraper

Fast, reliable, and simple BLS economic data scraping with intelligent caching.

## Features

- **High Performance**: Optimized caching with sub-second repeated requests
- **Reliable Sources**: FRED CSV primary + BLS historical backup 
- **Simple API**: Just `load_data(ticker, date)`
- **Smart Caching**: 1-hour cache for maximum speed
- **Anti-Detection**: Realistic browser headers to avoid blocking

## Quick Start

```python
from bls_scraper import load_data

# Load CPI data
cpi_data = load_data('cpi', '2022-2024')

# Load Core CPI (without food/energy)  
core_cpi = load_data('cpi_core', '2023')

# Load unemployment rate
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

## Files

- `bls_scraper.py` - Main unified scraper
- `main.py` - Command line interface
- `requirements.txt` - Dependencies
- `data_cache/` - Cached data (auto-created)

## Architecture

Single file design with:
- Unified scraper class
- Intelligent caching system
- Multiple data sources with fallbacks
- Anti-detection features
- Simple API interface