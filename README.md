# BLS Economic Data API

production-ready fastapi for us bureau of labor statistics economic data

## Quick Start (2 Commands)

```bash
pip install -r requirements.txt
python run.py
```

done! api running at `http://localhost:8000`

## What You Get

- fastapi with automatic docs at `/docs`
- economic data: cpi, ppi, unemployment, etc.
- smart caching for instant responses
- csv exports for data analysis
- zero configuration required

## Usage Examples

```bash
# Get CPI data
curl "http://localhost:8000/data/cpi?date=2022-2024"

# Get unemployment rate
curl "http://localhost:8000/data/unemployment?date=2023"

# Export as CSV
curl "http://localhost:8000/data/cpi?format=csv" -o cpi_data.csv

# Check health
curl "http://localhost:8000/health"
```

## Python Usage

```python
import requests

# Your original load_data function, now as API
response = requests.get('http://localhost:8000/data/cpi?date=2022-2024')
data = response.json()['data']

print(f"Latest CPI: {data[0]['value']} ({data[0]['date']})")
```

## Available Endpoints

- `GET /` - API information
- `GET /docs` - Interactive documentation  
- `GET /data/{ticker}` - Economic data (CPI, PPI, unemployment, etc.)
- `GET /indicators` - List all available indicators
- `GET /health` - Health check
- `GET /stats` - Performance statistics
- `POST /clear-cache` - Clear cache

## File Structure

- `bls_api.py` - Complete API with built-in BLS scraper
- `run.py` - Simple startup script
- `requirements.txt` - Dependencies

that's it! just 3 files for a complete production api.

## Configuration (Optional)

Set environment variables to customize:

```bash
PORT=8000          # Server port
HOST=0.0.0.0       # Server host  
CACHE_TTL=3600     # Cache duration (1 hour)
MAX_RESULTS=1000   # Max results per request
```

## Ready for Production

built-in caching system  
error handling & logging  
health checks & monitoring  
automatic api documentation  
csv export capability  
concurrent request handling  
bls data scraping built-in  

perfect for your colleague! same functionality as your original `load_data(ticker, date)` function, now as a production api.