# BLS Scraper API - Production Deployment Guide

## Quick Start for Colleagues

### Option 1: Local Development Setup
```bash
# Clone the repository
git clone <repository-url>
cd BLS-Scraper-API

# Install dependencies
pip install -r requirements.txt

# Run the API server
python app.py
```

API will be available at: `http://localhost:5000`

### Option 2: Docker Deployment (Recommended)
```bash
# Build the Docker image
docker build -t bls-scraper-api .

# Run the container
docker run -p 5000:5000 bls-scraper-api
```

## API Usage Examples

### 1. Get CPI Data
```bash
curl "http://localhost:5000/data/cpi?date=2022-2024"
```

### 2. Get Available Indicators
```bash
curl "http://localhost:5000/indicators"
```

### 3. Health Check
```bash
curl "http://localhost:5000/health"
```

### 4. Python Client Example
```python
import requests

# Get CPI data
response = requests.get('http://localhost:5000/data/cpi?date=2022-2024')
data = response.json()

print(f"Status: {data['status']}")
print(f"Data points: {data['count']}")
print(f"Latest CPI: {data['data'][0]['value']}")
```

## Production Deployment Options

### 1. Cloud Platform (Heroku, Railway, Render)

#### Heroku Deployment:
```bash
# Install Heroku CLI and login
heroku login

# Create app
heroku create your-bls-scraper-api

# Deploy
git push heroku main
```

#### Railway Deployment:
1. Connect your GitHub repository
2. Railway auto-detects Python and deploys
3. No additional configuration needed

### 2. VPS/Server Deployment

#### Using Gunicorn (Production WSGI server):
```bash
# Install gunicorn (already in requirements.txt)
pip install gunicorn

# Run with gunicorn
gunicorn --bind 0.0.0.0:5000 --workers 4 app:app
```

#### Using systemd service:
```bash
# Create service file: /etc/systemd/system/bls-scraper.service
[Unit]
Description=BLS Scraper API
After=network.target

[Service]
User=www-data
WorkingDirectory=/path/to/your/app
ExecStart=/path/to/your/venv/bin/gunicorn --bind 0.0.0.0:5000 --workers 4 app:app
Restart=always

[Install]
WantedBy=multi-user.target

# Enable and start service
sudo systemctl enable bls-scraper
sudo systemctl start bls-scraper
```

### 3. Docker Deployment

#### Basic Docker Run:
```bash
docker build -t bls-scraper-api .
docker run -d -p 5000:5000 --name bls-api bls-scraper-api
```

#### Docker Compose:
```yaml
# docker-compose.yml
version: '3.8'
services:
  bls-api:
    build: .
    ports:
      - "5000:5000"
    environment:
      - HOST=0.0.0.0
      - PORT=5000
    volumes:
      - ./data_cache:/app/data_cache
    restart: unless-stopped
```

## Configuration

### Environment Variables
Create a `.env` file (copy from `.env.example`):
```bash
HOST=0.0.0.0
PORT=5000
FLASK_DEBUG=False
CACHE_HOURS=1
LOG_LEVEL=INFO
```

### Production Considerations

1. **Caching**: Data is cached for 1 hour by default
2. **Rate Limiting**: Consider adding rate limiting for public APIs
3. **HTTPS**: Use a reverse proxy (nginx) or cloud load balancer for HTTPS
4. **Monitoring**: API includes health check endpoint at `/health`
5. **Logging**: Logs are written to `bls_api.log`

## API Endpoints Reference

| Endpoint | Method | Description |
|----------|---------|-------------|
| `/` | GET | API information |
| `/health` | GET | Health check |
| `/indicators` | GET | Available economic indicators |
| `/data/<ticker>` | GET | Get economic data |
| `/clear-cache` | POST | Clear data cache |

### Query Parameters for `/data/<ticker>`:
- `date`: Date range (e.g., "2022-2024", "2023", "last 3 years")
- `format`: Output format ("json" or "csv")

## Available Economic Indicators

- `cpi` - Consumer Price Index All Items
- `cpi_core` - Core CPI (less food/energy)
- `cpi_food` - Food CPI
- `cpi_energy` - Energy CPI
- `cpi_housing` - Housing CPI
- `ppi` - Producer Price Index
- `unemployment` - Unemployment Rate
- `gdp` - Gross Domestic Product

## Troubleshooting

### Common Issues:

1. **Port already in use**: Change PORT in .env file
2. **No data returned**: Check ticker name and date format
3. **Cache issues**: Call `/clear-cache` endpoint
4. **Permission errors**: Ensure cache directory is writable

### Logs:
- Check `bls_api.log` for detailed error messages
- Use `/health` endpoint to verify system status

## Performance Optimization

- **Cache**: Data cached for 1 hour (configurable)
- **Fresh data**: 2-5 seconds typical response time
- **Cached data**: <0.1 seconds response time
- **Concurrent requests**: Supports multiple workers with gunicorn

## Security Notes

- API uses CORS headers for cross-origin requests
- No authentication by default (add if needed)
- Docker container runs as non-root user
- Input validation on all parameters