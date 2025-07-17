# BLS Scraper API - Quick Start Guide

## 🚀 Get Started in 5 Minutes

This guide will help you clone and run the BLS Scraper API locally, then integrate it into your own Python scripts.

## 📋 Prerequisites

- Python 3.8+ installed
- Git installed
- Internet connection

## 🔧 Installation

### Step 1: Clone the Repository
```bash
git clone https://github.com/yourusername/bls-scraper-api.git
cd "BLS Scraper API"
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

That's it! Only 3 lightweight dependencies are required:
- `requests` - For web scraping
- `beautifulsoup4` - For HTML parsing
- `lxml` - For XML/HTML processing

### Step 3: Test the Installation
```bash
python -c "from app.fast_bls_api import load_data; print('✅ Installation successful!')"
```

## 🎯 Quick Usage Examples

### Option 1: Fast Cached Data (Recommended)
```python
from app.fast_bls_api import load_data

# Get CPI data in milliseconds
cpi_data = load_data('cpi', '2020-2024')
print(f"Latest CPI: {cpi_data[0]['value']} ({cpi_data[0]['date']})")
print(f"Found {len(cpi_data)} data points")
```

### Option 2: Live Fresh Data
```python
from app.live_bls_scraper import load_data

# Get fresh data from BLS website (takes 1-3 seconds)
fresh_data = load_data('cpi', '2024')
print(f"Fresh CPI: {fresh_data[0]['value']}")
print(f"Scraped at: {fresh_data[0]['scraped_at']}")
```

### Option 3: Professional Standardized Format
```python
from app.fast_bls_api import load_data

# Get data in professional hedge fund format
response = load_data('cpi', '2024', standardized=True)
print(f"Success: {response['success']}")
print(f"Latest CPI: {response['data'][0]['value']}")
print(f"Data quality: {response['metadata']['quality']}")
print(f"API version: {response['metadata']['api_version']}")
```

## 📊 Available Economic Data

### Consumer Price Index (CPI)
```python
cpi_all = load_data('cpi', '2024')           # All items
cpi_core = load_data('cpi_core', '2024')     # Less food & energy
cpi_energy = load_data('cpi_energy', '2024') # Energy prices
cpi_housing = load_data('cpi_housing', '2024') # Housing costs
```

### Producer Price Index (PPI)
```python
ppi_all = load_data('ppi', '2024')           # All manufacturing
ppi_core = load_data('ppi_core', '2024')     # Core manufacturing
ppi_energy = load_data('ppi_energy', '2024') # Energy commodities
```

### Other Economic Indicators
```python
unemployment = load_data('unemployment', '2024') # Unemployment rate
```

## 📅 Date Format Options

```python
# Single year
data = load_data('cpi', '2024')

# Year range
data = load_data('cpi', '2020-2024')

# Recent years
data = load_data('cpi', 'last 3 years')

# Default (last 3 years)
data = load_data('cpi')
```

## 🔄 Integration Examples

### Example 1: Simple Script Integration
Create `my_analysis.py`:
```python
#!/usr/bin/env python3
"""
Example: Integrate BLS API into your own script
"""
import sys
import os

# Add the BLS API to your path
sys.path.append('/path/to/BLS Scraper API')

from app.fast_bls_api import load_data

def analyze_inflation():
    """Analyze recent inflation trends"""
    
    # Get recent CPI data
    cpi_data = load_data('cpi', '2022-2024')
    
    if not cpi_data:
        print("❌ Failed to load CPI data")
        return
    
    # Calculate year-over-year inflation
    latest = cpi_data[0]
    year_ago = None
    
    for point in cpi_data:
        if point['year'] == latest['year'] - 1 and point['month'] == latest['month']:
            year_ago = point
            break
    
    if year_ago:
        inflation_rate = ((latest['value'] - year_ago['value']) / year_ago['value']) * 100
        print(f"📈 Current CPI: {latest['value']} ({latest['date']})")
        print(f"📉 Year-over-year inflation: {inflation_rate:.2f}%")
    
    return cpi_data

if __name__ == "__main__":
    analyze_inflation()
```

### Example 2: Trading Strategy Integration
```python
#!/usr/bin/env python3
"""
Example: Use BLS data in a trading strategy
"""
from app.fast_bls_api import load_data
from app.live_bls_scraper import load_data as load_fresh

def inflation_trading_signal():
    """Generate trading signals based on inflation data"""
    
    # Get both CPI and PPI data
    cpi_data = load_data('cpi', '2024')
    ppi_data = load_data('ppi', '2024')
    
    if not cpi_data or not ppi_data:
        return "NO_SIGNAL"
    
    # Simple logic: if PPI > CPI, inflation pressure building
    latest_cpi = cpi_data[0]['value']
    latest_ppi = ppi_data[0]['value']
    
    # Calculate month-over-month changes
    cpi_change = ((cpi_data[0]['value'] - cpi_data[1]['value']) / cpi_data[1]['value']) * 100
    ppi_change = ((ppi_data[0]['value'] - ppi_data[1]['value']) / ppi_data[1]['value']) * 100
    
    if ppi_change > cpi_change and ppi_change > 0.2:
        return "INFLATION_PRESSURE_BUILDING"
    elif cpi_change < -0.1:
        return "DEFLATIONARY_SIGNAL"
    else:
        return "NEUTRAL"

def main():
    signal = inflation_trading_signal()
    print(f"🎯 Trading Signal: {signal}")
    
    # Get fresh data for confirmation
    fresh_cpi = load_fresh('cpi', '2024')
    if fresh_cpi:
        print(f"🔄 Fresh CPI: {fresh_cpi[0]['value']} (scraped {fresh_cpi[0]['scraped_at']})")

if __name__ == "__main__":
    main()
```

### Example 3: Data Analysis with Pandas
```python
#!/usr/bin/env python3
"""
Example: Convert BLS data to pandas DataFrame for analysis
"""
import pandas as pd
from app.fast_bls_api import load_data

def create_economic_dashboard():
    """Create a comprehensive economic data DataFrame"""
    
    # Load multiple economic indicators
    indicators = {
        'CPI': load_data('cpi', '2020-2024'),
        'Core_CPI': load_data('cpi_core', '2020-2024'),
        'PPI': load_data('ppi', '2020-2024'),
        'Unemployment': load_data('unemployment', '2020-2024')
    }
    
    # Convert to pandas DataFrames
    dfs = {}
    for name, data in indicators.items():
        if data:
            df = pd.DataFrame(data)
            df['date'] = pd.to_datetime(df['date'])
            df = df.set_index('date').sort_index()
            dfs[name] = df[['value']].rename(columns={'value': name})
    
    # Combine all indicators
    combined_df = pd.concat(dfs.values(), axis=1)
    
    # Calculate correlations
    correlations = combined_df.corr()
    print("📊 Economic Indicator Correlations:")
    print(correlations)
    
    # Calculate year-over-year changes
    yoy_changes = combined_df.pct_change(periods=12) * 100
    print("\n📈 Year-over-Year Changes (%):")
    print(yoy_changes.tail())
    
    return combined_df

if __name__ == "__main__":
    df = create_economic_dashboard()
```

## 🔍 Testing Your Installation

### Run Built-in Tests
```bash
# Test basic functionality
python -c "
from app.fast_bls_api import load_data
from app.live_bls_scraper import load_data as load_live

print('Testing cached API...')
cpi = load_data('cpi', '2024')
print(f'✅ Cached API: {len(cpi) if cpi else 0} data points')

print('Testing live scraper...')
fresh = load_live('cpi', '2024')
print(f'✅ Live scraper: {len(fresh) if fresh else 0} data points')

print('✅ All tests passed!')
"
```

### Run the Demo Dashboard
```bash
python simple_bls_dashboard.py
```

This will show you:
- Performance comparison of all APIs
- Statistical analysis of economic data
- ASCII charts of trends
- Export capabilities

## 📁 Project Structure

```
BLS Scraper API/
├── app/
│   ├── fast_bls_api.py              # Fast cached data API
│   ├── live_bls_scraper.py          # Live web scraping API
│   ├── standardized_schema.py       # Professional data format
│   └── ultra_fresh_scraper.py       # Multi-source fresh data
├── cached_data/                     # Pre-cached BLS data files
│   ├── CPIAUCSL_latest.json
│   ├── CPILFESL_latest.json
│   └── PPIFIS_latest.json
├── scripts/                         # Utility scripts
│   ├── export_cpi_ppi_csv.py
│   └── polars_demo.py
├── docs/                           # Documentation
├── requirements.txt                # Dependencies
├── QUICK_START_GUIDE.md           # This file
├── STANDARDIZED_DATA_SCHEMA.md    # Professional format docs
├── simple_bls_dashboard.py        # Demo dashboard
└── README.md                      # Main documentation
```

## 🚀 Performance Characteristics

| API Type | Speed | Data Freshness | Use Case |
|----------|--------|----------------|----------|
| **Fast Cached** | 0-1ms | Historical + Recent | High-frequency analysis, backtesting |
| **Live Scraper** | 50-300ms | Always fresh | Real-time trading, current data |
| **Ultra Fresh** | 300-500ms | Multi-source verified | Critical decisions, data validation |

## 🔧 Configuration Options

### Advanced Usage with Custom Settings
```python
from app.fast_bls_api import FastBLSAPI
from app.live_bls_scraper import LiveBLSScraper

# Custom cache directory
fast_api = FastBLSAPI(cache_dir="my_custom_cache", max_workers=20)

# Custom scraper settings
live_api = LiveBLSScraper(max_workers=10)

# Load data with custom settings
data = fast_api.load_data('cpi', '2024', standardized=True)
```

## 🛠️ Troubleshooting

### Common Issues

**1. Import Error**
```bash
# Error: ModuleNotFoundError: No module named 'app'
# Solution: Make sure you're in the project root directory
cd "BLS Scraper API"
python -c "from app.fast_bls_api import load_data"
```

**2. No Data Returned**
```python
# Check if cached data exists
import os
print(os.listdir('cached_data/'))  # Should show .json files

# Try different date ranges
data = load_data('cpi', '2020-2024')  # Broader range
```

**3. Slow Live Scraping**
```python
# Use cached data for better performance
from app.fast_bls_api import load_data  # Fast version
data = load_data('cpi', '2024')  # Milliseconds response
```

## 📞 Support

- Check the main `README.md` for detailed usage
- Review `STANDARDIZED_DATA_SCHEMA.md` for professional format
- Run `simple_bls_dashboard.py` for a working example
- Look at scripts in the `scripts/` folder for more examples

## 🎯 Next Steps

1. **Run the quick test** to verify installation
2. **Try the demo dashboard** to see all features
3. **Integrate into your scripts** using the examples above
4. **Use standardized format** for professional applications
5. **Explore the cached data** in `cached_data/` folder

The API is designed to be **simple, fast, and professional** - perfect for hedge funds, trading systems, and economic analysis! 