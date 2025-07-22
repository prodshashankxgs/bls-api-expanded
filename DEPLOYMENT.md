# BLS Scraper API - Production Ready

## quick start for your colleague

your bls scraper api is now streamlined and production-ready! here's everything they need:

### Install & Run (2 simple steps)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start the API
python start.py
```

that's it! the api will be running at `http://localhost:8000`

## 📖 API Documentation

interactive docs: `http://localhost:8000/docs` (automatic openapi documentation)

## 🔧 Core Files (Only 3 files needed!)

1. **`api.py`** - Main FastAPI application with all functionality
2. **`start.py`** - Simple startup script 
3. **`bls_scraper.py`** - Your original BLS scraper (unchanged)

## 🌐 API Endpoints

### Get Economic Data (Your original load_data function!)
```bash
# CPI data
curl "http://localhost:8000/data/cpi?date=2022-2024"

# Unemployment data  
curl "http://localhost:8000/data/unemployment?date=2023"

# Core CPI
curl "http://localhost:8000/data/cpi_core?date=2024"
```

### Export as CSV
```bash
curl "http://localhost:8000/data/cpi?date=2024&format=csv" -o cpi_data.csv
```

### Available Endpoints
- `GET /` - API information
- `GET /health` - Health check
- `GET /docs` - Interactive documentation
- `GET /indicators` - List all available indicators
- `GET /data/{ticker}` - Get economic data
- `GET /stats` - Performance statistics
- `POST /clear-cache` - Clear cache

## 💡 Usage Examples

### From Command Line
```bash
# Get latest CPI data
curl "http://localhost:8000/data/cpi?date=2024"

# Get unemployment with limit
curl "http://localhost:8000/data/unemployment?date=2023&limit=50"
```

### From Python
```python
import requests

# Get CPI data (same as your original load_data function!)
response = requests.get("http://localhost:8000/data/cpi?date=2022-2024")
cpi_data = response.json()['data']

print(f"Latest CPI: {cpi_data[0]['value']} ({cpi_data[0]['date']})")
```

### From JavaScript/Browser
```javascript
fetch('http://localhost:8000/data/cpi?date=2024')
  .then(response => response.json())
  .then(data => console.log(data.data));
```

## 🎯 Production Features

✅ **FastAPI with automatic documentation**  
✅ **Intelligent caching system (memory + file)**  
✅ **Concurrent request handling**  
✅ **Error handling & validation**  
✅ **Performance monitoring**  
✅ **Health checks**  
✅ **CSV export support**  
✅ **Production logging**  
✅ **Zero-config startup**  

## ⚡ Performance

- **Cache warming** on startup for instant responses
- **Memory + file caching** for optimal speed
- **Concurrent processing** for multiple requests
- **Automatic cache management** with TTL
- **Performance stats** at `/stats` endpoint

## 🔧 Configuration (Optional)

Create a `.env` file to customize (copy from `.env.example`):

```bash
PORT=8000          # Server port
HOST=0.0.0.0       # Server host
WORKERS=4          # Number of workers
CACHE_TTL=3600     # Cache time-to-live (1 hour)
MAX_RESULTS=1000   # Max results per request
LOG_LEVEL=INFO     # Logging level
```

## 🔍 Available Economic Indicators

- `cpi` - Consumer Price Index (All Items)
- `cpi_core` - Core CPI (without food/energy)
- `cpi_food` - Food CPI
- `cpi_energy` - Energy CPI  
- `cpi_housing` - Housing CPI
- `ppi` - Producer Price Index
- `unemployment` - Unemployment Rate
- And more! (See `/indicators` endpoint)

## 📊 Monitoring

### Health Check
```bash
curl http://localhost:8000/health
```

### Performance Stats
```bash
curl http://localhost:8000/stats
```

### Clear Cache (if needed)
```bash
curl -X POST http://localhost:8000/clear-cache
```

## 🚨 Troubleshooting

**Port already in use?**
- Change PORT in `.env` file or set environment variable: `PORT=8001 python start.py`

**Missing dependencies?**
- Run: `pip install -r requirements.txt`

**Permission errors?**
- Ensure write access to the directory for cache creation

## 🎯 Perfect for Your Colleague

Your original `load_data(ticker, date)` function is now a production API:

**Before:** `load_data('cpi', '2022-2024')`  
**Now:** `GET /data/cpi?date=2022-2024`

- Same functionality, now accessible over HTTP
- Interactive documentation at `/docs`
- Automatic caching for speed
- CSV export capability
- Production-ready error handling
- Zero configuration required

---

ready to ship to your colleague! just send them `api.py`, `start.py`, and `requirements.txt`