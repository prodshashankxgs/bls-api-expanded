# BLS Data API

A Python FastAPI wrapper for the Bureau of Labor Statistics (BLS) API that provides enhanced economic data with calculated insights and friendly series names.

## Features

- **Friendly Series Names**: Use simple names like `unemployment`, `inflation`, `jobs`, `wages`, and `productivity` instead of complex BLS series IDs
- **Enhanced Calculations**: Automatic month-over-month and year-over-year change calculations
- **Trend Analysis**: Simple trend indicators (increasing, decreasing, stable)
- **Caching**: In-memory caching for improved performance
- **Multi-Series Comparison**: Compare two economic indicators side-by-side
- **Economic Dashboard**: Get key economic indicators in a single call
- **Error Handling**: Comprehensive error handling with helpful messages

## Available Economic Series

| Series Name | Description | Units | BLS Series ID |
|-------------|-------------|-------|---------------|
| `unemployment` | Unemployment Rate | Percent | LNS14000000 |
| `inflation` | Consumer Price Index - All Urban Consumers | Index 1982-84=100 | CUUR0000SA0 |
| `jobs` | Total Nonfarm Employment | Thousands of Persons | CES0000000001 |
| `wages` | Average Hourly Earnings - Private Sector | Dollars per Hour | CES0500000003 |
| `productivity` | Nonfarm Business Sector Productivity | Index 2012=100 | PRS85006092 |

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd BLS\ Scraper\ API
```

2. Create a virtual environment and install dependencies:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install fastapi uvicorn httpx python-dotenv pydantic requests
```

3. (Optional) Set up your BLS API key:
   - Create a `.env` file in the root directory
   - Add your BLS API key: `BLS_API_KEY=your_api_key_here`
   - Register for a free API key at: https://www.bls.gov/developers/api_signature_v2.html

## Usage

### Starting the Server

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

### API Endpoints

#### Root Endpoint
- **GET /** - API information and available endpoints

#### Health Check
- **GET /health** - API health status and configuration

#### Series Data
- **GET /data/{series_name}** - Get enhanced data for a specific series
  - `series_name`: One of: unemployment, inflation, jobs, wages, productivity
  - `years`: Number of years of data (1-10, default: 3)
  - `enhanced`: Include calculated fields (default: true)

#### Series Comparison
- **GET /compare** - Compare two economic series
  - `series1`: First series to compare (default: unemployment)
  - `series2`: Second series to compare (default: inflation)
  - `years`: Years of data for comparison (1-5, default: 2)

#### Economic Dashboard
- **GET /dashboard** - Get key economic indicators in one call

#### Available Series
- **GET /series** - List all available series with descriptions

#### Cache Management
- **GET /cache/status** - View cache status
- **DELETE /cache/clear** - Clear cached data

### Example Usage

```bash
# Get unemployment data for the last 3 years
curl http://localhost:8000/data/unemployment

# Get inflation data for 2 years without enhancements
curl http://localhost:8000/data/inflation?years=2&enhanced=false

# Compare unemployment vs inflation
curl http://localhost:8000/compare?series1=unemployment&series2=inflation

# Get economic dashboard
curl http://localhost:8000/dashboard
```

### Enhanced Data Fields

The API adds value over raw BLS data by calculating:
- `month_change`: Month-over-month percentage change
- `year_change`: Year-over-year percentage change
- `trend`: Simple trend indicator (increasing, decreasing, stable)

### Response Format

```json
{
  "series_name": "unemployment",
  "series_id": "LNS14000000",
  "title": "Unemployment Rate",
  "units": "Percent",
  "data": [
    {
      "date": "2024-01-01",
      "value": 3.9,
      "period": "M01",
      "year": 2024,
      "month_change": -0.1,
      "year_change": 0.5,
      "trend": "stable"
    }
  ],
  "last_updated": "2024-01-15",
  "total_points": 36,
  "fetch_time_seconds": 0.234,
  "cached": false
}
```

## Testing

Run the test script to verify all endpoints:

```bash
python app/test_api.py
```

This will test all endpoints and demonstrate the API's functionality including caching performance.

## Project Structure

```
BLS Scraper API/
├── app/
│   ├── main.py          # FastAPI application and endpoints
│   ├── bls_client.py    # BLS API client
│   ├── models.py        # Pydantic data models
│   └── test_api.py      # Test script
└── README.md
```

## Dependencies

- **FastAPI**: Web framework for building APIs
- **Uvicorn**: ASGI server for running the application
- **httpx**: Async HTTP client for BLS API requests
- **Pydantic**: Data validation and serialization
- **python-dotenv**: Environment variable management

## Configuration

Environment variables:
- `BLS_API_KEY`: Your BLS API registration key (optional, increases rate limits)

## Rate Limits

- **Without API key**: 25 requests per day
- **With API key**: 500 requests per day

## Error Handling

The API provides comprehensive error handling:
- Invalid series names return 404 with available options
- BLS API errors are caught and returned with helpful messages
- Network errors are handled gracefully
- Global exception handler for unexpected errors

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source. Please ensure compliance with BLS API terms of service when using this wrapper.