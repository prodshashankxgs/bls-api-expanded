# BLS Scraper API - Complete Deployment Guide

A platform-agnostic FastAPI solution for accessing Bureau of Labor Statistics data from any system.

## 📁 Project Files Overview

### Core API Files
- **`api.py`** - Main FastAPI web service
- **`bls_client.py`** - Simple client module for consuming the API
- **`BLS_API_Test_Notebook.ipynb`** - Comprehensive Jupyter notebook for testing

### Original Application Files
- **`config.py`** - Configuration management
- **`scraper.py`** - BLS data scraper
- **`data.py`** - Data access functions
- **`load_data.py`** - Enhanced data loading
- **`bls_package.py`** - Portable package module
- **`run.py`** - Application runner

## 🚀 Quick Start (5 Minutes)

### Step 1: Start the API Server (Host Machine)
```bash
# Navigate to the project directory
cd "BLS Scraper API"

# Install API dependencies (if not already installed)
pip install fastapi uvicorn

# Download initial BLS data
python run.py

# Start the API server
python api.py
```
**Server will be running at:** `http://localhost:8000`

### Step 2: Test the API
Open your browser and visit: `http://localhost:8000`
You should see the interactive API documentation.

### Step 3: Use from Another Project
Copy these files to your new project:
- `bls_client.py` 
- `BLS_API_Test_Notebook.ipynb`

## 💻 Client Usage (Any System)

### Method 1: Using the BLS Client (Recommended)
```python
# Copy bls_client.py to your project
from bls_client import BLSClient

# Connect to your API server
client = BLSClient("http://192.168.1.100:8000")  # Replace with your IP

# Get data
df = client.get_data(["All items", "Food", "Energy"], "2025-06")
print(df)
```

### Method 2: Direct HTTP Requests
```python
import requests
import pandas as pd

# Make API request
response = requests.post("http://192.168.1.100:8000/data", json={
    "categories": ["All items", "Food", "Energy"],
    "date": "2025-06"
})

# Process response
if response.status_code == 200:
    result = response.json()
    if result["success"]:
        df = pd.DataFrame(result["data"])
        print(df)
```

### Method 3: Browser Access
Visit these URLs directly in your browser:
- API docs: `http://your-ip:8000/`
- Health check: `http://your-ip:8000/health`
- Sample data: `http://your-ip:8000/data/All%20items,Food/2025-06`

## 🌐 Network Access Setup

### For Local Network Access
1. **Find your IP address:**
   ```bash
   # Windows
   ipconfig | findstr IPv4
   
   # Mac/Linux
   ifconfig | grep inet
   ```

2. **Start server on all interfaces:**
   ```bash
   # Edit api.py or run directly:
   python -c "
   import uvicorn; 
   from api import app; 
   uvicorn.run(app, host='0.0.0.0', port=8000)
   "
   ```

3. **Share your IP with colleagues:**
   ```
   http://192.168.1.100:8000  # Replace with your actual IP
   ```

### Firewall Settings
- **Windows:** Allow Python through Windows Firewall
- **Mac:** System Preferences → Security & Privacy → Firewall → Allow incoming connections
- **Linux:** `sudo ufw allow 8000`

## 📊 Using the Jupyter Notebook

1. **Copy files to your new project:**
   ```
   your-project/
   ├── bls_client.py
   └── BLS_API_Test_Notebook.ipynb
   ```

2. **idk ngl**

3. **Update the API URL in the notebook:**
   ```python
   API_URL = "http://192.168.1.100:8000"  # Change to your server's IP
   ```

4. **Run all cells** - the notebook includes:
   - Connection testing
   - Data loading examples
   - Inflation analysis
   - Visualizations
   - Export functionality

## 🛠️ API Endpoints Reference

| Endpoint | Method | Description | Example |
|----------|--------|-------------|---------|
| `/` | GET | Interactive API docs | `http://localhost:8000/` |
| `/health` | GET | Health check | `http://localhost:8000/health` |
| `/categories` | GET | Available categories | `http://localhost:8000/categories` |
| `/data` | POST | Load data (recommended) | See JSON example below |
| `/data/{categories}/{date}` | GET | Load data via URL | `http://localhost:8000/data/All%20items,Food/2025-06` |
| `/status` | GET | Detailed status | `http://localhost:8000/status` |
| `/download` | GET | Download latest data | `http://localhost:8000/download` |

### POST Request Example:
```json
POST /data
Content-Type: application/json

{
  "categories": ["All items", "Food", "Energy", "Shelter"],
  "date": "2025-06"
}
```

### Response Format:
```json
{
  "success": true,
  "data": [
    {
      "category": "All items",
      "nsa_current_month": 310.3,
      "nsa_previous_month": 309.1,
      "current_month": "2025-06",
      "previous_month": "2025-05"
    }
  ],
  "message": "Successfully loaded data for 4 categories",
  "metadata": {...}
}
```

## 🔧 Troubleshooting

### Common Issues and Solutions

**❌ "Cannot connect to API server"**
- ✅ Make sure `python api.py` is running
- ✅ Check if port 8000 is blocked by firewall
- ✅ Verify the correct IP address in client code

**❌ "No data available"**
- ✅ Run `python run.py` to download BLS data first
- ✅ Check `/status` endpoint for data availability

**❌ "Import error: cannot import bls_client"**
- ✅ Make sure `bls_client.py` is in your project directory
- ✅ Check Python path with `import sys; print(sys.path)`

**❌ "Network timeout"**
- ✅ Increase timeout in client: `requests.post(..., timeout=60)`
- ✅ Check network connectivity: `ping your-server-ip`

**❌ "Categories not found"**
- ✅ Use exact category names from `/categories` endpoint
- ✅ Check spelling and capitalization

### Debug Commands
```bash
# Test server locally
curl http://localhost:8000/health

# Test from another machine
curl http://192.168.1.100:8000/health

# Check if port is in use
# Windows: netstat -an | findstr 8000
# Mac/Linux: lsof -i :8000

# Test data endpoint
curl -X POST http://localhost:8000/data \
  -H "Content-Type: application/json" \
  -d '{"categories": ["All items"], "date": "2025-06"}'
```

## 📱 Client Dependencies

**Minimal requirements for clients:**
```bash
pip install requests pandas
```

**For full notebook functionality:**
```bash
pip install requests pandas matplotlib seaborn jupyter
```

## 🔒 Security Notes

This setup is designed for development/internal use. For production:
- Add authentication (API keys, OAuth)
- Use HTTPS with proper certificates
- Implement rate limiting
- Add input validation and sanitization
- Set up proper logging and monitoring

## 📞 Support

**If your colleague has issues:**

1. **Share this exact checklist:**
   - [ ] Can you access `http://your-ip:8000/health` in browser?
   - [ ] Do you have `requests` and `pandas` installed?
   - [ ] Is `bls_client.py` in your project directory?
   - [ ] Are you using the correct API URL?

2. **Common fixes:**
   - Restart the API server: `python api.py`
   - Check firewall settings on host machine
   - Try localhost first: `http://localhost:8000`
   - Use IP instead of hostname

3. **Test with browser first** before using Python code

## ✨ What Your Colleague Can Do

With this setup, your colleague can:
- Access BLS inflation data from her Windows laptop
- Use the data in Jupyter notebooks with full visualizations
- Run analysis scripts in any Python environment
- Access the API via browser for quick data checks
- Export results to CSV/Excel
- Build her own applications using the API

**No complex setup required on her end - just copy 2 files and install 2 packages!**