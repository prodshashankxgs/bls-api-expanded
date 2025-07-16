#!/usr/bin/env python3
"""
High-Frequency CPI/PPI Trading API
===================================

FastAPI server optimized for real-time CPI and PPI data for trading.
Designed to provide 1-minute speed advantage over Bloomberg.

Endpoints:
- /cpi/{ticker} - Get CPI data
- /ppi/{ticker} - Get PPI data  
- /inflation/latest - Get latest key inflation indicators
- /inflation/dashboard - Trading dashboard with alerts
- /inflation/alerts - Current inflation alerts
- /indicators - List all available indicators
"""

import sys
import os
import logging
from datetime import datetime, date
from typing import Dict, List, Optional, Union
import uvicorn
from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Add parent directory to path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from high_frequency_cpi_ppi_loader import HighFrequencyCPIPPILoader, InflationAlert

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="High-Frequency CPI/PPI Trading API",
    description="Real-time inflation data for trading - 1-minute advantage over Bloomberg",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the high-frequency loader
hf_loader = HighFrequencyCPIPPILoader()

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "api": "High-Frequency CPI/PPI Trading API",
        "version": "1.0.0",
        "description": "Real-time inflation data for trading",
        "advantage": "1-minute speed over Bloomberg",
        "endpoints": {
            "cpi": "/cpi/{ticker}",
            "ppi": "/ppi/{ticker}", 
            "latest": "/inflation/latest",
            "dashboard": "/inflation/dashboard",
            "alerts": "/inflation/alerts",
            "indicators": "/indicators"
        },
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "fred_loader": "operational",
            "inflation_data": "available",
            "trading_ready": True
        }
    }

@app.get("/cpi/{ticker}")
async def get_cpi_data(
    ticker: str,
    date_param: Optional[str] = Query(None, description="Specific date (YYYY-MM-DD) or None for latest"),
    force_refresh: bool = Query(True, description="Force fresh data scrape")
):
    """
    Get CPI data for a specific indicator
    
    Examples:
    - /cpi/CPI_ALL - All Urban Consumers CPI
    - /cpi/CPI_CORE - Core CPI (ex food & energy)  
    - /cpi/CPI_HOUSING - Housing CPI
    """
    try:
        # Ensure ticker has CPI prefix
        if not ticker.upper().startswith('CPI_'):
            ticker = f"CPI_{ticker.upper()}"
        
        data = hf_loader.load_data(ticker, date_param, force_refresh)
        
        if not data:
            raise HTTPException(status_code=404, detail=f"CPI data not found for {ticker}")
        
        # Build response
        response = {
            "ticker": ticker,
            "series_id": data.series_id,
            "title": data.title,
            "units": data.units,
            "frequency": data.frequency,
            "source": data.source,
            "data_summary": {
                "total_points": len(data.data_points),
                "date_range": {
                    "start": data.data_points[0].date if data.data_points else None,
                    "end": data.data_points[-1].date if data.data_points else None
                },
                "latest_value": data.data_points[-1].value if data.data_points else None,
                "latest_date": data.data_points[-1].date if data.data_points else None
            }
        }
        
        # Include full data if requested
        if date_param or len(data.data_points) <= 12:  # Include full data for specific dates or recent data
            response["data_points"] = [
                {
                    "date": point.date,
                    "value": point.value,
                    "year": point.year,
                    "month": point.month
                }
                for point in data.data_points
            ]
        
        return response
        
    except Exception as e:
        logger.error(f"Error loading CPI data for {ticker}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ppi/{ticker}")
async def get_ppi_data(
    ticker: str,
    date_param: Optional[str] = Query(None, description="Specific date (YYYY-MM-DD) or None for latest"),
    force_refresh: bool = Query(True, description="Force fresh data scrape")
):
    """
    Get PPI data for a specific indicator
    
    Examples:
    - /ppi/PPI_ALL - All Commodities PPI
    - /ppi/PPI_FINAL_DEMAND - Final Demand PPI (most watched)
    - /ppi/PPI_ENERGY - Energy PPI
    """
    try:
        # Ensure ticker has PPI prefix
        if not ticker.upper().startswith('PPI_'):
            ticker = f"PPI_{ticker.upper()}"
        
        data = hf_loader.load_data(ticker, date_param, force_refresh)
        
        if not data:
            raise HTTPException(status_code=404, detail=f"PPI data not found for {ticker}")
        
        # Build response
        response = {
            "ticker": ticker,
            "series_id": data.series_id,
            "title": data.title,
            "units": data.units,
            "frequency": data.frequency,
            "source": data.source,
            "data_summary": {
                "total_points": len(data.data_points),
                "date_range": {
                    "start": data.data_points[0].date if data.data_points else None,
                    "end": data.data_points[-1].date if data.data_points else None
                },
                "latest_value": data.data_points[-1].value if data.data_points else None,
                "latest_date": data.data_points[-1].date if data.data_points else None
            }
        }
        
        # Include full data if requested
        if date_param or len(data.data_points) <= 12:  # Include full data for specific dates or recent data
            response["data_points"] = [
                {
                    "date": point.date,
                    "value": point.value,
                    "year": point.year,
                    "month": point.month
                }
                for point in data.data_points
            ]
        
        return response
        
    except Exception as e:
        logger.error(f"Error loading PPI data for {ticker}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/inflation/latest")
async def get_latest_inflation(
    force_refresh: bool = Query(True, description="Force fresh data scrape")
):
    """
    Get latest values for key inflation indicators
    
    Returns the most recent CPI and PPI values for trading decisions.
    """
    try:
        key_indicators = [
            'CPI_ALL', 'CPI_CORE', 'PPI_FINAL_DEMAND', 'PPI_ALL',
            'CPI_HOUSING', 'CPI_ENERGY', 'PPI_ENERGY'
        ]
        
        logger.info("Loading latest inflation data for trading...")
        latest_values = hf_loader.get_latest_values(key_indicators, force_refresh)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "indicators": latest_values,
            "summary": {
                "total_indicators": len(latest_values),
                "cpi_indicators": len([k for k in latest_values.keys() if k.startswith('CPI_')]),
                "ppi_indicators": len([k for k in latest_values.keys() if k.startswith('PPI_')])
            },
            "note": "Values are latest available from FRED (faster than Bloomberg)"
        }
        
    except Exception as e:
        logger.error(f"Error getting latest inflation data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/inflation/dashboard")
async def get_trading_dashboard(
    force_refresh: bool = Query(True, description="Force fresh data scrape")
):
    """
    Get comprehensive CPI/PPI trading dashboard
    
    Includes latest values, changes, and alerts for key indicators.
    """
    try:
        logger.info("Building inflation trading dashboard...")
        dashboard = hf_loader.get_trading_dashboard(force_refresh)
        
        return dashboard
        
    except Exception as e:
        logger.error(f"Error building trading dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/inflation/alerts")
async def get_inflation_alerts(
    force_refresh: bool = Query(True, description="Force fresh data scrape")
):
    """
    Get current inflation alerts for significant changes
    
    Returns alerts for CPI/PPI changes that could move markets.
    """
    try:
        # Get dashboard to extract alerts
        dashboard = hf_loader.get_trading_dashboard(force_refresh)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "alerts": dashboard['alerts'],
            "summary": {
                "total_alerts": dashboard['summary']['total_alerts'],
                "critical_alerts": dashboard['summary']['critical_alerts'],
                "alert_levels": {
                    "INFO": len([a for a in dashboard['alerts'] if a['alert_level'] == 'INFO']),
                    "WARNING": len([a for a in dashboard['alerts'] if a['alert_level'] == 'WARNING']),
                    "CRITICAL": len([a for a in dashboard['alerts'] if a['alert_level'] == 'CRITICAL'])
                }
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting inflation alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/indicators")
async def get_available_indicators():
    """
    Get all available CPI and PPI indicators
    
    Returns comprehensive list of supported inflation indicators.
    """
    try:
        indicators = hf_loader.get_available_indicators()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "indicators": indicators,
            "summary": {
                "total_cpi": len(indicators['cpi_indicators']),
                "total_ppi": len(indicators['ppi_indicators']),
                "total_indicators": len(indicators['cpi_indicators']) + len(indicators['ppi_indicators'])
            },
            "usage": {
                "cpi_endpoint": "/cpi/{ticker}",
                "ppi_endpoint": "/ppi/{ticker}",
                "examples": [
                    "/cpi/CPI_ALL",
                    "/ppi/PPI_FINAL_DEMAND",
                    "/cpi/CPI_CORE",
                    "/ppi/PPI_ENERGY"
                ]
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting available indicators: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/compare/{ticker1}/{ticker2}")
async def compare_indicators(
    ticker1: str,
    ticker2: str,
    force_refresh: bool = Query(True, description="Force fresh data scrape")
):
    """
    Compare two inflation indicators
    
    Examples:
    - /compare/CPI_ALL/PPI_FINAL_DEMAND
    - /compare/CPI_CORE/CPI_ALL
    """
    try:
        # Load both indicators
        data1 = hf_loader.load_data(ticker1, force_refresh=force_refresh)
        data2 = hf_loader.load_data(ticker2, force_refresh=force_refresh)
        
        if not data1:
            raise HTTPException(status_code=404, detail=f"Data not found for {ticker1}")
        if not data2:
            raise HTTPException(status_code=404, detail=f"Data not found for {ticker2}")
        
        # Get latest values
        latest1 = data1.data_points[-1] if data1.data_points else None
        latest2 = data2.data_points[-1] if data2.data_points else None
        
        comparison = {
            "timestamp": datetime.now().isoformat(),
            "indicator1": {
                "ticker": ticker1,
                "series_id": data1.series_id,
                "latest_value": latest1.value if latest1 else None,
                "latest_date": latest1.date if latest1 else None
            },
            "indicator2": {
                "ticker": ticker2,
                "series_id": data2.series_id,
                "latest_value": latest2.value if latest2 else None,
                "latest_date": latest2.date if latest2 else None
            }
        }
        
        # Calculate comparison metrics
        if latest1 and latest2:
            comparison["comparison"] = {
                "ratio": latest1.value / latest2.value if latest2.value != 0 else None,
                "difference": latest1.value - latest2.value,
                "percent_difference": ((latest1.value - latest2.value) / latest2.value) * 100 if latest2.value != 0 else None
            }
        
        return comparison
        
    except Exception as e:
        logger.error(f"Error comparing {ticker1} and {ticker2}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/refresh/{ticker}")
async def refresh_indicator(
    ticker: str,
    background_tasks: BackgroundTasks
):
    """
    Force refresh of a specific indicator in the background
    """
    def refresh_data():
        try:
            logger.info(f"Background refresh for {ticker}")
            hf_loader.load_data(ticker, force_refresh=True)
        except Exception as e:
            logger.error(f"Background refresh failed for {ticker}: {e}")
    
    background_tasks.add_task(refresh_data)
    
    return {
        "message": f"Background refresh initiated for {ticker}",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    print("🔥 Starting High-Frequency CPI/PPI Trading API...")
    print("=" * 60)
    print("📊 Real-time inflation data for trading")
    print("⚡ 1-minute speed advantage over Bloomberg")
    print("🚀 Access via: http://localhost:8001")
    print("📖 Documentation: http://localhost:8001/docs")
    print("=" * 60)
    
    # Run the server
    uvicorn.run(
        "cpi_ppi_trading_api:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    ) 