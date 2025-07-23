# BLS Data Scraper - Perfect Two-Tab Workflow 🚀

This guide shows exactly how to run your BLS data scraper for the smoothest workflow possible.

## 🎯 **The Perfect Setup**

### **Tab 1: Auto-Scraper (Keep Running)**
```bash
python3 auto_scraper.py
```
**What it does:**
- ✅ Monitors BLS website every 30 minutes during business hours
- ✅ Automatically downloads new Excel files when BLS releases data
- ✅ Processes and validates data in real-time
- ✅ Shows live status dashboard
- ✅ Keeps your data fresh without any manual work

### **Tab 2: Your Analysis (Use Data Immediately)**
```python
from data_loader import DataLoader

# Your exact usage pattern works immediately!
tickers = ["CPSCJEWE Index", "CPIQWAN Index", "CPSCWG Index", "CPSCMB Index", "CPSCINTD Index", "CPIQSMFN Index"]
dl = DataLoader()
df = dl.load_data(tickers, "2025-01-01")
print(df)
```

---

## 🚀 **Quick Start (2 Minutes)**

### 1. **Start the Auto-Scraper**
Open VSCode terminal tab #1:
```bash
cd "BLS Scraper API"
python3 auto_scraper.py
```

You'll see:
```
🏛️  BLS AUTO-SCRAPER
==================================================
🎯 Monitoring BLS for new Excel files...
📊 Your data will be automatically updated!
💻 Keep this tab running, use data in another tab
🔄 Checks every hour during business hours
📈 Real-time processing and validation
==================================================

🔍 Checking BLS website for new files...
✅ Processed 39 rows, 11 columns
📈 DATA UPDATE SUMMARY
📊 Total categories: 39
🚀 Ready for use! Try: load_data('CPSCJEWE Index', 'latest')
```

**✅ Leave this tab running!**

### 2. **Use Your Data Immediately**
Open VSCode terminal tab #2 (or Python script):
```python
from data_loader import DataLoader

# Your exact pattern works immediately!
tickers = ["CPSCJEWE Index", "CPIQWAN Index", "CPSCWG Index"]  
dl = DataLoader()
df = dl.load_data(tickers, "latest")

print(f"✅ Loaded {df.shape[0]} rows of fresh BLS data!")
print(df.head())
```

**🎉 That's it! Your data is live and updating automatically!**

---

## 📊 **Data Usage Examples**

### **Basic Usage (Your Pattern)**
```python
from data_loader import DataLoader

# Exactly what you wanted
tickers = ["CPSCJEWE Index", "CPIQWAN Index", "CPSCWG Index", "CPSCMB Index", "CPSCINTD Index", "CPIQSMFN Index"]
dl = DataLoader()
df = dl.load_data(tickers, "2025-01-01")

# Your data is ready!
print(f"Shape: {df.shape}")
print(f"Categories: {df['category'].unique()}")
```

### **Quick Functions**
```python
from data_loader import load_data

# Individual tickers
headline_cpi = load_data("CPSCJEWE Index", "latest")
core_cpi = load_data("CPIQWAN Index", "latest") 
food_cpi = load_data("Food", "latest")
```

### **Advanced Client**
```python
from data_loader import BLSDataClient

client = BLSDataClient()

# Get data with caching
df = client.get_data("CPSCJEWE Index", use_cache=True)

# Search capabilities
clothing_data = client.search_categories("clothing")
all_categories = client.get_categories()

# Complete dataset
full_data = client.get_complete_dataset()
```

---

## ⚡ **When New BLS Data is Released**

### **What Happens Automatically:**
1. **Tab 1 (auto_scraper.py)** detects new Excel file
2. Downloads it automatically
3. Processes and validates the data  
4. Updates your local data files
5. Shows summary of new data

### **What You Do:**
1. **Nothing!** Just keep using your `load_data()` functions
2. Your functions automatically use the freshest data
3. No restarts, no manual downloads, no interruptions

### **Example:**
```
# Tab 1 shows:
✅ New file downloaded: cpi-news-release-table1-202507.xlsx
📊 Processing new file: cpi-news-release-table1-202507.xlsx
✅ Processed 42 rows, 11 columns
🚀 Ready for use! Try: load_data('CPSCJEWE Index', 'latest')

# Tab 2 instantly gets fresh data:
df = load_data("CPSCJEWE Index", "latest")  # ← Uses July data automatically!
```

---

## 🛠️ **Alternative Running Options**

### **Option 1: Manual Server (Original)**
```bash
python3 run.py
# Then use: http://localhost:8000/docs
```

### **Option 2: One-Time Data Check**
```bash
python3 quick_start.py
# Shows demo and current data status
```

### **Option 3: Manual Download**
```python
from xlsx_loader import BLSExcelDownloader

downloader = BLSExcelDownloader()
file_path = downloader.download_latest_cpi_file()
print(f"Downloaded: {file_path}")
```

---

## 📈 **Data Sources & Fallbacks**

Your system intelligently uses **3 data sources**:

1. **🥇 Excel Files (Primary)**: Fresh BLS supplemental files
2. **🥈 BLS API (Fallback)**: Additional series when Excel doesn't have them  
3. **🥉 Sample Data (Fallback)**: Realistic data when API limits hit

### **Smart Data Flow:**
```
Excel File → BLS API → Sample Data
    ↓           ↓          ↓
  Real Data   Real Data   Sample
   (Fresh)   (Historical) (Realistic)
```

**Your `load_data()` functions automatically choose the best available source!**

---

## 🎯 **Perfect for Your Use Case**

### **✅ What This Solves:**
- **Auto-Updates**: New BLS data flows in automatically
- **Zero Downtime**: Your analysis never stops
- **Simple Interface**: Your exact `load_data()` pattern works
- **Fresh Data**: Always the latest when BLS releases
- **No Manual Work**: Set it and forget it

### **🚀 Production Ready:**
- **Error Handling**: Graceful fallbacks when things fail
- **Caching**: Fast repeated access
- **Scheduling**: Smart business-hours checking
- **Validation**: Ensures data quality
- **Logging**: Full visibility into what's happening

---

## 🔧 **Configuration Options**

### **Auto-Scraper Settings:**
Edit `auto_scraper.py` to customize:
```python
# Check frequency (default: every 30 minutes during business hours)
schedule.every().hour.at(":00").do(self.check_for_updates)
schedule.every().hour.at(":30").do(self.check_for_updates)

# Business hours (default: 9 AM - 6 PM ET)
for hour in range(9, 19):
    # ...
```

### **Data Loader Settings:**
Edit `data_loader.py` to customize:
```python
# Cache duration (default: 1 hour)
client = BLSDataClient(cache_ttl=3600)

# Excel file age threshold (default: 6 hours)
if file_age < timedelta(hours=6):
    # ...
```

---

## 📋 **Troubleshooting**

### **Auto-Scraper Not Running?**
```bash
# Check if it's running
ps aux | grep auto_scraper

# Restart it
python3 auto_scraper.py
```

### **No Data Loading?**
```python
# Check system status
from data_loader import DataLoader
dl = DataLoader()
print(dl.health_check())
print(dl.get_excel_info())
```

### **BLS API Rate Limited?**
- **Normal**: System automatically falls back to sample data
- **Solution**: Wait 24 hours for API reset
- **Excel data**: Still works perfectly!

---

## 🎉 **You're Ready!**

### **Perfect Workflow:**
1. **Start**: `python3 auto_scraper.py` in Tab 1
2. **Use**: Your `load_data()` functions in Tab 2  
3. **Enjoy**: Fresh economic data automatically!

### **Your Code Works Exactly As You Want:**
```python
from data_loader import DataLoader

tickers = ["CPSCJEWE Index", "CPIQWAN Index", "CPSCWG Index", "CPSCMB Index", "CPSCINTD Index", "CPIQSMFN Index"]
dl = DataLoader()
df = dl.load_data(tickers, "2025-01-01")

# ✅ This works immediately with fresh data!
# ✅ Updates automatically when BLS releases new files!
# ✅ No manual work required!
```

**Your BLS economic data pipeline is production-ready! 📊🚀** 