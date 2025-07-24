# 🚀 Quick Setup Guide - BLS API Client

Use the BLS API from a completely separate project with just 2 files!

## 🎯 What You Want to Achieve

- Run `api.py` in **Project A** (BLS Scraper API folder)
- Use `load_data(ticker, date)` in **Project B** (your analysis project)
- Pass ALL tickers from Excel sheet to get complete DataFrame
- Print the DataFrame in Jupyter notebook

## 📁 File Setup

### Project A (BLS Scraper API) - Server Side
```
BLS Scraper API/
├── api.py          ← Run this to start the server
├── scraper.py      
├── data_sheet/     ← Excel files downloaded here
└── ... (all other files)
```

### Project B (Your Analysis) - Client Side
```
my-analysis-project/
├── bls_client.py           ← Copy this file from Project A
├── simple_bls_notebook.ipynb  ← Copy this file from Project A
└── your_analysis.ipynb     ← Your custom notebooks
```

## 🔧 Step-by-Step Setup

### Step 1: Start the API Server (Project A)
```bash
cd "BLS Scraper API"

# Download data first (if not already done)
python run.py

# Start the API server
python api.py
```
✅ Server runs at: `http://localhost:8000`

### Step 2: Copy Files to Your Project (Project B)
Copy these 2 files from Project A to Project B:
- `bls_client.py`
- `simple_bls_notebook.ipynb`

### Step 3: Install Dependencies (Project B)
```bash
pip install requests pandas
```

### Step 4: Use in Your Project

#### Option A: Jupyter Notebook (Recommended)
1. Open `simple_bls_notebook.ipynb`
2. Run all cells
3. See complete DataFrame printed!

#### Option B: Python Script
```python
from bls_client import load_data, get_all_tickers

# Get all available tickers
all_tickers = get_all_tickers()
print(f"Found {len(all_tickers)} tickers")

# Load data for ALL tickers
df = load_data(all_tickers, "2025-06")

# Print the complete DataFrame
print(df)
```

## 🎯 Exact Usage Pattern You Want

```python
# This is exactly what you wanted:
from bls_client import load_data, get_all_tickers

# Step 1: Get all tickers from Excel sheet
ticker = get_all_tickers()  # Returns list of ALL tickers

# Step 2: Load data for all tickers
df = load_data(ticker, "2025-06")  # Returns pandas DataFrame

# Step 3: Print DataFrame
print(df)
```

## 🌐 Network Usage (Optional)

If Project A and Project B are on different computers:

### Project A (Server):
```bash
# Find your IP address
# Windows: ipconfig
# Mac/Linux: ifconfig

# Start server on all interfaces
python -c "
import uvicorn
from api import app
uvicorn.run(app, host='0.0.0.0', port=8000)
"
```

### Project B (Client):
```python
# Update the API URL
from bls_client import load_data, get_all_tickers

API_URL = "http://192.168.1.100:8000"  # Replace with actual IP

ticker = get_all_tickers(API_URL)
df = load_data(ticker, "2025-06", API_URL)
print(df)
```

## 🔍 Available Data Columns

The DataFrame will contain columns like:
- `category` - The ticker name (e.g., "All items", "Food")
- `nsa_current_month` - Current month NSA value
- `nsa_previous_month` - Previous month NSA value  
- `sa_current_month` - Current month SA value (if available)
- `sa_previous_month` - Previous month SA value (if available)
- `current_month` - Date string (e.g., "2025-06")
- `previous_month` - Date string (e.g., "2025-05")

## 🆘 Troubleshooting

**❌ "Cannot connect to BLS API"**
- Make sure `python api.py` is running in Project A
- Check the API URL (http://localhost:8000)

**❌ "Import Error: cannot import bls_client"**
- Make sure `bls_client.py` is in your Project B folder

**❌ "No data available"**
- Run `python run.py` in Project A to download data first

**❌ Empty ticker list**
- Check that Excel files exist in Project A's `data_sheet/` folder

## ✅ Success Check

You'll know it's working when you see:
```
✅ Connected to BLS API at http://localhost:8000
   Data available: True
📊 Retrieved 99 available tickers
✅ Successfully loaded data for 99 tickers
📋 Complete BLS Data for 2025-06:
================================================================================
    category  nsa_current_month  nsa_previous_month  ...
0  All items              310.3               309.1  ...
1       Food              320.1               318.9  ...
...
```

That's it! You now have a complete pandas DataFrame with ALL the BLS data ready for analysis! 🎉 