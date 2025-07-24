# BLS Data API - Platform Agnostic Deployment

A simple FastAPI web service for accessing Bureau of Labor Statistics Consumer Price Index data from any system.

## Quick Start

### 1. Start the API Server (Host System)

```bash
# Navigate to the project directory
cd "BLS Scraper API"

# Install dependencies
pip install fastapi uvicorn requests pandas

# Download initial data
python run.py

# Start the API server
python api.py
```

The API will be available at: `http://localhost:8000`

### 2. Access from Any System (Client)

Your colleague can access the API from Windows, Mac, or Linux:

```python
# client_example.py - Copy this file to any system
import requests
import pandas as pd

# Create client
class BLSDataClient:
    def __init__(self, base_url="http://YOUR_IP:8000"):
        self.base_url = base_url
    
    def load_data(self, categories, date):
        response = requests.post(f"{self.base_url}/data", json={
            "categories": categories,
            "date": date
        })
        result = response.json()
        return pd.DataFrame(result["data"]) if result["success"] else None

# Usage
client = BLSDataClient("http://192.168.1.100:8000")  # Replace with actual IP
df = client.load_data(["All items", "Food", "Energy"], "2025-06")
print(df)
```

## API Endpoints

### Health Check
```bash
GET http://localhost:8000/health
```

### Get Available Categories
```bash
GET http://localhost:8000/categories?limit=20
```

### Load Data (POST)
```bash
POST http://localhost:8000/data
Content-Type: application/json

{
  "categories": ["All items", "Food", "Energy"],
  "date": "2025-06"
}
```

### Load Data (GET)
```bash
GET http://localhost:8000/data/All%20items,Food,Energy/2025-06
```

### Get Status
```bash
GET http://localhost:8000/status
```

### Download Latest Data
```bash
GET http://localhost:8000/download
```

## Network Access Setup

### For Local Network Access

1. **Find your IP address:**
   ```bash
   # Windows
   ipconfig
   
   # Mac/Linux  
   ifconfig
   ```

2. **Start server on all interfaces:**
   ```bash
   python -c "
   import uvicorn
   from api import app
   uvicorn.run(app, host='0.0.0.0', port=8000)
   "
   ```

3. **Access from other machines:**
   ```
   http://192.168.1.100:8000  # Replace with your actual IP
   ```

### For Internet Access (Advanced)

1. **Use ngrok for temporary public access:**
   ```bash
   # Install ngrok: https://ngrok.com/
   python api.py  # Start the API
   
   # In another terminal:
   ngrok http 8000
   
   # Share the ngrok URL (e.g., https://abc123.ngrok.io)
   ```

## Example Usage Scenarios

### Jupyter Notebook (Client Side)
```python
import requests
import pandas as pd
import matplotlib.pyplot as plt

# Connect to API
api_url = "http://192.168.1.100:8000"  # Replace with actual URL

# Load data
response = requests.post(f"{api_url}/data", json={
    "categories": ["All items", "Food", "Energy", "Shelter"],
    "date": "2025-06"
})

# Process data
data = response.json()["data"]
df = pd.DataFrame(data)

# Calculate inflation
df['inflation'] = ((df['nsa_current_month'] - df['nsa_previous_month']) 
                   / df['nsa_previous_month'] * 100)

# Plot
plt.figure(figsize=(10, 6))
plt.barh(df['category'], df['inflation'])
plt.title('Month-over-Month Inflation by Category')
plt.xlabel('Inflation Rate (%)')
plt.show()
```

### Python Script (Client Side)
```python
# simple_client.py
import requests
import json

def get_inflation_data(api_url, categories, date):
    response = requests.post(f"{api_url}/data", json={
        "categories": categories,
        "date": date
    })
    
    if response.status_code == 200:
        result = response.json()
        if result["success"]:
            return result["data"]
    
    return None

# Usage
api_url = "http://192.168.1.100:8000"
categories = ["All items", "Food", "Energy"]
data = get_inflation_data(api_url, categories, "2025-06")

if data:
    for item in data:
        category = item['category']
        prev = item['nsa_previous_month']
        curr = item['nsa_current_month']
        change = ((curr - prev) / prev * 100)
        print(f"{category}: {prev:.1f} → {curr:.1f} ({change:+.2f}%)")
```

### cURL Commands
```bash
# Health check
curl http://localhost:8000/health

# Get categories
curl http://localhost:8000/categories

# Load data
curl -X POST http://localhost:8000/data \
  -H "Content-Type: application/json" \
  -d '{"categories": ["All items", "Food"], "date": "2025-06"}'

# Load data (GET method)
curl "http://localhost:8000/data/All%20items,Food/2025-06"
```

## Troubleshooting

### Server Won't Start
- Check if port 8000 is in use: `lsof -i :8000` (Mac/Linux) or `netstat -an | findstr 8000` (Windows)
- Try a different port: `uvicorn api:app --port 8001`

### No Data Available
- Run `python run.py` to download BLS data
- Check `GET /status` endpoint for data availability

### Network Access Issues
- Check firewall settings
- Ensure the server is running on `0.0.0.0:8000`, not `127.0.0.1:8000`
- Verify IP address is correct

### Client Connection Issues
- Test with browser first: `http://YOUR_IP:8000/health`
- Verify the API URL in client code
- Check network connectivity: `ping YOUR_IP`

## Security Note

This API is designed for internal/development use. For production deployment, consider:
- Adding authentication
- Using HTTPS
- Implementing rate limiting
- Adding input validation
- Setting up proper logging

## Dependencies

**Server Side:**
- Python 3.7+
- fastapi
- uvicorn
- pandas
- requests
- beautifulsoup4
- openpyxl

**Client Side:**
- Python 3.7+
- requests
- pandas (optional)
- matplotlib (optional)