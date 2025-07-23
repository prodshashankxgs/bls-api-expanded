# BLS Economic Data Scraper API

A production-ready Python application for extracting and serving US Bureau of Labor Statistics (BLS) economic data. Features a FastAPI backend with web scraping capabilities and a clean Python interface for data analysis.

## 🚀 Quick Start

### 1. Installation

```bash
# Navigate to project directory
cd BLS-Scraper-API

# Install dependencies
pip install -r requirements.txt
```

### 2. Start the API Server

```bash
# Start the BLS API server
python3 run.py
```

Server starts on `http://localhost:8000` with docs at `http://localhost:8000/docs`

### 3. Use the Clean Interface

```python
from data_loader import DataLoader

# Your colleague's exact usage pattern
tickers = ["cpi", "unemployment", "ppi"]
dl = DataLoader()
df = dl.load_data(tickers, "2023-2025")
print(df)
```

## 📊 Available Economic Indicators

| Ticker | Description | Coverage |
|--------|-------------|----------|
| `cpi` | Consumer Price Index | 1913-Present |
| `cpi_core` | Core CPI (Less Food/Energy) | 1957-Present |
| `cpi_food` | Food Consumer Price Index | 1913-Present |
| `cpi_energy` | Energy Consumer Price Index | 1957-Present |
| `cpi_housing` | Housing Consumer Price Index | 1952-Present |
| `ppi` | Producer Price Index | 1947-Present |
| `unemployment` | Unemployment Rate | 1948-Present |

## 💻 Usage Examples

### Basic Usage (Your Colleague's Pattern)

```python
from data_loader import DataLoader

# Exact interface your colleague expects
tickers = ["cpi", "unemployment"]
dl = DataLoader()
df = dl.load_data(tickers, "2022-2025")
print(df)

# Get summary statistics
summary = dl.get_summary(df)
print(summary)
```

### Advanced Analysis

```python
# Load multiple indicators
indicators = ["cpi", "cpi_core", "unemployment", "ppi"]
df = dl.load_data(indicators, "2020-2025")

# Convert to wide format for time series analysis
wide_df = dl.get_wide_format(df)

# Save data
dl.save_data(df, "economic_data.csv")
dl.save_data(wide_df, "economic_data_wide.csv")
```

### Quick Functions

```python
from data_loader import load_cpi_data, load_unemployment_data

# Quick access to common indicators
cpi = load_cpi_data("2023-2025")
unemployment = load_unemployment_data("2023-2025")
```

## 🏗️ System Architecture

```
BLS Website → Web Scraper → FastAPI Server → Data Loader → Your Analysis
```

### Key Components:
- **`data_loader.py`** - Clean interface (what your colleague uses)
- **`bls_api.py`** - FastAPI server with BLS scraping
- **`run.py`** - Server startup script

## 📈 Data Format

All data returned as Polars DataFrames with:

| Column | Description | Example |
|--------|-------------|---------|
| `ticker` | Indicator code | "cpi" |
| `category` | Full name | "Consumer Price Index" |
| `period` | Human date | "January 2025" |
| `date` | Standard date | 2025-01-01 |
| `value` | Actual index/rate | 322.561 |
| `year` | Year | 2025 |
| `month` | Month | 1 |

### Value Types:
- **CPI/PPI**: Actual index numbers (base 1982-84=100)
- **Unemployment**: Actual percentage rate

## ⚙️ Configuration

### Optional Environment Variables
```bash
export BLS_API_PORT=8000
export BLS_CACHE_TTL=3600
export BLS_MAX_RESULTS=1000
```

## 🚨 Troubleshooting

### Server Connection Issues
```bash
# Make sure server is running
python3 run.py

# Test server health
curl http://localhost:8000/health
```

### No Data Found
```python
# Check available indicators
dl = DataLoader()
print(dl.get_available_indicators())

# Test server connection
print(dl.health_check())
```

## 📁 Project Files

**Core Files:**
- `data_loader.py` - Main interface for your colleague
- `bls_api.py` - API server and web scraper
- `run.py` - Server startup
- `requirements.txt` - Dependencies
- `README.md` - This file

**Auto-Generated:**
- `data_cache/` - Cached data (improves performance)
- `*.csv` - Data exports

## 🌐 API Endpoints (Optional)

Direct API access if needed:
- `GET /data/{ticker}?date=2023-2025` - Get economic data
- `GET /indicators` - List available indicators
- `GET /health` - Health check
- `GET /docs` - Interactive documentation

## 🎯 Ready for Your Colleague

The `data_loader.py` provides exactly the interface your colleague expects:

```python
from data_loader import DataLoader

# Their exact usage pattern works
tickers = ["CPSCJEWE Index", "CPIQWAN Index"]  # Will map to supported tickers
dl = DataLoader()
df = dl.load_data(tickers, "2025-01-01")
print(df)
```

**Features:**
- ✅ Clean Python interface
- ✅ Polars DataFrame output
- ✅ Historical data from 1913
- ✅ Automatic caching
- ✅ Error handling
- ✅ Multiple export formats
- ✅ Production-ready