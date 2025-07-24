# BLS Economic Data Scraper

A cross-platform, easy-to-use scraper for US Bureau of Labor Statistics economic data. Downloads Excel files automatically and provides simple functions to access CPI and inflation data.

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Download Data
```bash
# Download once and exit
python scraper.py

# Download continuously (checks every 30 minutes)
python scraper.py continuous

# Download and show sample data
python scraper.py data
```

### 3. Use Data in Python
```python
from data import get_cpi, get_food_data, get_energy_data, print_summary

# Get CPI data
cpi_data = get_cpi()
print(cpi_data.head())

# Get specific categories
food_prices = get_food_data()
energy_prices = get_energy_data()
housing_prices = get_housing_data()

# Quick summary
print_summary()
```

## Features

✅ **Cross-platform** - Works on Windows, Mac, and Linux  
✅ **Automatic downloads** - Gets latest Excel files from BLS website  
✅ **Easy to use** - Simple functions that return pandas DataFrames  
✅ **Human-readable** - Clear code that's easy to understand and modify  
✅ **Configurable** - Customize paths with environment variables  

## Project Structure

```
BLS Scraper API/
├── config.py          # Cross-platform configuration
├── scraper.py          # Main scraper (downloads Excel files)
├── data.py             # Data access functions
├── requirements.txt    # Python dependencies
├── xlsx_loader/        # Excel processing utilities
├── data_sheet/         # Downloaded Excel files (auto-created)
├── data_cache/         # Cached data (auto-created)
└── logs/              # Log files (auto-created)
```

## Configuration

The scraper uses `config.py` to handle paths and settings. It automatically detects your operating system and creates the right file paths.

### Environment Variables (Optional)
```bash
# Customize data directories
export BLS_DATA_SHEET_DIR=/path/to/excel/files
export BLS_CACHE_DIR=/path/to/cache
export BLS_LOG_LEVEL=DEBUG
```

### Windows Example
```cmd
set BLS_DATA_SHEET_DIR=C:\BLS_Data
set BLS_CACHE_DIR=C:\BLS_Cache
```

## Available Data Functions

```python
from data import *

# Core functions
cpi_data = get_cpi()                    # Consumer Price Index
all_data = get_all_data()              # Everything in latest file

# Category-specific functions  
food_data = get_food_data()            # Food prices
energy_data = get_energy_data()        # Energy prices
housing_data = get_housing_data()      # Housing/shelter costs

# Custom categories
transport_data = get_inflation_data("Transportation")
clothing_data = get_inflation_data("Apparel")

# Summary and analysis
summary = quick_summary()              # Dict with key metrics
print_summary()                        # Pretty-printed summary
```

## Example Output

```bash
$ python scraper.py
🏛️  Starting BLS Scraper
📁 Data directory: /Users/me/BLS_Data/data_sheet
📁 Cache directory: /Users/me/BLS_Data/data_cache
✅ Scraper ready!
🔍 Checking BLS website for new files...
📊 Currently have 1 Excel files
✅ Downloaded new file: news-release-table1-202507.xlsx
⏱️  Download took 3.45 seconds
📋 Processing news-release-table1-202507.xlsx
✅ Processed 89 data points
⏱️  Processing took 0.82 seconds

==================================================
📊 BLS SCRAPER STATUS
==================================================
📁 Excel files: 2
📥 Files downloaded this session: 1
🔍 Last check: 14:30:25
📥 Last download: 14:30:28
📄 Latest file: news-release-table1-202507.xlsx (14:30:28)
==================================================
```

## Data Summary Example

```python
from data import print_summary
print_summary()
```

```
========================================
📊 INFLATION SUMMARY
========================================
Headline Cpi   : 3.2
Food           : 2.1
Energy         : 4.5
Shelter        : 5.8
========================================
```

## Troubleshooting

### No Excel files found
1. Run `python scraper.py` first to download files
2. Check that directories exist: `python -c "from config import Config; Config.print_configuration()"`

### Path issues on Windows
Make sure you're using forward slashes or the config system:
```python
from config import Config
data_dir = Config.DATA_SHEET_DIR  # Automatically correct for your OS
```

### Test everything is working
```python
from data import test_functions
test_functions()
```

## Dependencies

- **pandas** - Data manipulation
- **openpyxl** - Excel file reading  
- **requests** - Web downloads
- **beautifulsoup4** - HTML parsing
- **python-dateutil** - Date handling

## How It Works

1. **Scraper** (`scraper.py`) monitors the BLS website for new Excel files
2. **Downloader** (`xlsx_loader/downloader.py`) downloads files from BLS supplemental files page
3. **Processor** (`xlsx_loader/processor.py`) extracts CPI data from Excel files
4. **Data functions** (`data.py`) provide easy access to the processed data
5. **Config** (`config.py`) handles cross-platform file paths and settings

The system is designed to be simple to understand, modify, and use while providing robust data access for economic analysis.