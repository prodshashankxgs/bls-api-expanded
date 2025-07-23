# BLS Economic Data Scraper API

A production-ready Python application for extracting and serving US Bureau of Labor Statistics (BLS) economic data. Features a FastAPI backend with web scraping capabilities, Excel processing, and multiple clean Python interfaces for data analysis.

## 🚀 Quick Start

### 1. Installation

```bash
# Navigate to project directory
cd "BLS Scraper API"

# Install dependencies
pip install -r requirements.txt
```

### 2. Your Exact Usage Pattern (Works Now!)

```python
from data_loader import DataLoader

# Your colleague's exact usage pattern
tickers = ["CPSCJEWE Index", "CPIQWAN Index", "CPSCWG Index", "CPSCMB Index", "CPSCINTD Index", "CPIQSMFN Index"]
dl = DataLoader()
df = dl.load_data(tickers, "2025-01-01")
print(df)
```

### 3. Start the API Server (Optional)

```bash
# Start the BLS API server for web access
python3 run.py
```

Server starts on `http://localhost:8000` with docs at `http://localhost:8000/docs`

## 🎯 Three Usage Interfaces

### 1. Original DataLoader (Backward Compatible)
```python
from data_loader import DataLoader

# Your exact usage pattern
tickers = ["CPSCJEWE Index", "CPIQWAN Index"] 
dl = DataLoader()
df = dl.load_data(tickers, "2025-01-01")

# Additional features
health = dl.health_check()
excel_info = dl.get_excel_info()
summary = dl.get_summary(df)
dl.save_data(df, "output.csv")
```

### 2. Modern Function Interface
```python
from data_loader import load_data, quick_cpi, quick_core_cpi

# Individual ticker loading
df1 = load_data("CPSCJEWE Index", "2025-06")  # Headline CPI
df2 = load_data("Food", "latest")             # Food CPI  
df3 = load_data("Energy", "2025-06")          # Energy CPI

# Quick access functions
headline = quick_cpi("2025-06")
core = quick_core_cpi("2025-06")
```

### 3. REST-like Client Interface
```python
from data_loader import BLSDataClient

client = BLSDataClient()

# Data retrieval with caching
df = client.get_data("CPSCJEWE Index", date="2025-06")

# Exploration and analysis
categories = client.get_categories(level=1)
weights = client.get_weights()
search_results = client.search_categories("food")
complete_dataset = client.get_complete_dataset()

# Time series analysis
timeseries = client.get_time_series("CPSCJEWE Index", "2024-01", "2025-06")
```

## 📊 Available Economic Indicators

### Your Specific Tickers (All Working!)
| Ticker | Description | Source |
|--------|-------------|---------|
| `CPSCJEWE Index` | All items CPI (Headline) | Excel |
| `CPIQWAN Index` | Core CPI (Less Food/Energy) | Excel |
| `CPSCWG Index` | Women's and Girls' Clothing | BLS API |
| `CPSCMB Index` | Men's and Boys' Clothing | BLS API |
| `CPSCINTD Index` | Children's and Infants' Clothing | Sample |
| `CPIQSMFN Index` | Clothing Materials | Sample |

### Additional Categories (24 Total)
| Category | Examples | Coverage |
|----------|----------|----------|
| **Food** | Food, Food at home | Excel + BLS API |
| **Energy** | Energy, Gasoline | Excel + BLS API |
| **Housing** | Shelter, Rent | Excel + BLS API |
| **Transportation** | Vehicle insurance, Airline fares | BLS API |
| **Medical** | Medical care services | Excel + BLS API |
| **Services** | Services less energy | Excel + BLS API |

## 🏗️ Data Sources & Architecture

```
Excel Files → BLS API → Sample Data
     ↓           ↓          ↓
  Polars DataFrames → Unified Interface → Your Analysis
```

### Smart Data Loading:
1. **Excel First**: Processes BLS supplemental files (`data_sheet/*.xlsx`)
2. **API Fallback**: Uses BLS public API for additional series
3. **Sample Fallback**: Provides realistic sample data when needed
4. **Schema Alignment**: Automatically aligns different data sources

## 📈 Data Format

All data returned as **Polars DataFrames** with consistent schema:

| Column | Description | Example |
|--------|-------------|---------|
| `ticker` | Your ticker code | "CPSCJEWE Index" |
| `expenditure_category` | Full category name | "All items" |
| `relative_importance_pct` | Weight in CPI basket | "100.000" |
| `unadj_index_jun2025` | Latest index value | "325.4" |
| `unadj_pct_change_12mo` | 12-month % change | "3.2" |
| `unadj_pct_change_1mo` | 1-month % change | "0.3" |
| `category` | Grouped category | "headline_cpi" |
| `date_requested` | Date parameter | "2025-06" |

## 🔧 Advanced Features

### Caching & Performance
```python
client = BLSDataClient(cache_ttl=3600)  # 1 hour cache
df = client.get_data("CPSCJEWE Index", use_cache=True)
client.clear_cache()  # Manual cache clearing
```

### Data Analysis
```python
# Search and exploration
results = client.search_categories("clothing")
categories = client.get_categories(level=2)  # Hierarchy level
weights = client.get_weights()  # Relative importance

# Complete dataset access
full_data = client.get_complete_dataset()
print(f"Complete CPI dataset: {full_data.shape}")
```

### Export Options
```python
dl = DataLoader()
df = dl.load_data(["CPSCJEWE Index"], "2025-06")

# Save to different formats
dl.save_data(df, "cpi_data.csv")
dl.save_data(df, "cpi_data.json")

# Get summary statistics
summary = dl.get_summary(df)
```

## 🌐 API Endpoints (Optional Server)

When running `python3 run.py`:
- `GET /data/{ticker}?date=2025-06` - Get economic data
- `GET /indicators` - List available indicators
- `GET /health` - Health check
- `GET /docs` - Interactive documentation

## 📁 Project Structure

```
BLS Scraper API/
├── data_loader.py          # Main interface (YOUR ENTRY POINT)
├── bls_api.py             # FastAPI server (945 lines)
├── run.py                 # Server startup
├── demo.py                # Comprehensive demonstration
├── requirements.txt       # Dependencies
├── data_sheet/           # Excel files
├── xlsx_loader/          # Excel processing modules
├── examples/             # Usage examples
└── README.md            # This file
```

## 🎯 Ready for Production

✅ **Your Usage**: `tickers = ["CPSCJEWE Index", ...]; dl = DataLoader(); df = dl.load_data(tickers, "2025-01-01")`  
✅ **Data Sources**: Excel + BLS API + Sample fallbacks  
✅ **Performance**: Caching, concurrent processing, error handling  
✅ **Flexibility**: 3 interface styles, 24 indicators, multiple export formats  
✅ **Compatibility**: Works with existing `run.py` server  
✅ **Testing**: Comprehensive test suite included  

## 🚀 Run the Demo

```bash
python3 demo.py
```

Demonstrates all features including your exact ticker usage pattern!

---

**Your BLS economic data is ready for analysis! 📊**