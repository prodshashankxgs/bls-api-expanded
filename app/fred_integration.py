"""
FastAPI Integration for FRED Data Loader
Provides REST API endpoints for accessing FRED economic data
"""

from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Optional, List, Dict, Any
from datetime import date, datetime
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Import our FRED data loader
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fred_data_loader import FREDDataLoader, load_data, SeriesData
from mirror_system import mirror_cache

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FRED loader
fred_loader = FREDDataLoader()

# Thread pool for CPU-bound operations
executor = ThreadPoolExecutor(max_workers=4)

app = FastAPI(
    title="FRED Data API",
    description="Real-time economic data from FRED with intelligent caching and fallbacks",
    version="2.0.0"
)


def run_sync_in_thread(func, *args, **kwargs):
    """Run synchronous function in thread pool"""
    loop = asyncio.get_event_loop()
    return loop.run_in_executor(executor, func, *args, **kwargs)


@app.get("/")
async def root():
    """API root with system status"""
    cache_stats = mirror_cache.get_cache_stats()
    
    return {
        "message": "FRED Data API - Real-time Economic Data",
        "version": "2.0.0",
        "features": [
            "Direct FRED website scraping",
            "Website mirroring for reliability", 
            "BLS API fallback",
            "Intelligent caching",
            "User agent rotation"
        ],
        "cache_status": {
            "entries": cache_stats.get("total_entries", 0),
            "size_mb": round(cache_stats.get("total_size_mb", 0), 2),
            "utilization": round(cache_stats.get("utilization_percent", 0), 1)
        },
        "available_tickers": fred_loader.get_available_tickers()[:10]  # Show first 10
    }


@app.get("/fred/{ticker}")
async def get_fred_data(
    ticker: str,
    date: Optional[str] = Query(None, description="Specific date (YYYY-MM-DD) or latest"),
    years_back: int = Query(3, ge=1, le=20, description="Years of historical data"),
    force_refresh: bool = Query(False, description="Force refresh from source"),
    include_raw: bool = Query(False, description="Include raw data points")
):
    """
    Get economic data for a specific ticker
    
    Examples:
    - /fred/GDP - Latest GDP data
    - /fred/UNEMPLOYMENT?years_back=5 - 5 years of unemployment data
    - /fred/CPI?date=2023-01-01 - CPI data up to specific date
    """
    try:
        # Parse date if provided
        date_param = None
        if date:
            try:
                date_param = datetime.strptime(date, '%Y-%m-%d').date()
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
        
        # Load data in thread pool
        data = await run_sync_in_thread(
            fred_loader.load_data,
            ticker,
            date_param,
            years_back,
            force_refresh
        )
        
        if not data:
            raise HTTPException(
                status_code=404, 
                detail=f"No data found for ticker '{ticker}'. Available tickers: {fred_loader.get_available_tickers()[:5]}"
            )
        
        # Build response
        response = {
            "ticker": ticker,
            "series_id": data.series_id,
            "title": data.title,
            "units": data.units,
            "frequency": data.frequency,
            "source": data.source,
            "last_updated": data.last_updated,
            "data_summary": {
                "total_points": len(data.data_points),
                "date_range": {
                    "start": data.data_points[0].date.isoformat() if data.data_points else None,
                    "end": data.data_points[-1].date.isoformat() if data.data_points else None
                },
                "latest_value": data.data_points[-1].value if data.data_points else None,
                "latest_date": data.data_points[-1].date.isoformat() if data.data_points else None
            }
        }
        
        # Include raw data if requested
        if include_raw:
            response["data_points"] = [
                {
                    "date": point.date.isoformat(),
                    "value": point.value,
                    "period": point.period,
                    "year": point.year,
                    "month": point.month
                }
                for point in data.data_points
            ]
        
        return response
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error loading data for {ticker}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/fred/{ticker}/latest")
async def get_latest_value(ticker: str):
    """Get just the latest value for a ticker - optimized for quick access"""
    try:
        data = await run_sync_in_thread(fred_loader.load_data, ticker)
        
        if not data or not data.data_points:
            raise HTTPException(status_code=404, detail=f"No data found for ticker '{ticker}'")
        
        latest_point = data.data_points[-1]
        
        return {
            "ticker": ticker,
            "series_id": data.series_id,
            "title": data.title,
            "units": data.units,
            "value": latest_point.value,
            "date": latest_point.date.isoformat(),
            "source": data.source,
            "cached": "cached" in data.source.lower()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting latest value for {ticker}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/fred/compare/{ticker1}/{ticker2}")
async def compare_series(
    ticker1: str,
    ticker2: str,
    years_back: int = Query(3, ge=1, le=10, description="Years of data to compare")
):
    """Compare two economic series"""
    try:
        # Load both series concurrently
        data1_task = run_sync_in_thread(fred_loader.load_data, ticker1, years_back=years_back)
        data2_task = run_sync_in_thread(fred_loader.load_data, ticker2, years_back=years_back)
        
        data1, data2 = await asyncio.gather(data1_task, data2_task)
        
        if not data1:
            raise HTTPException(status_code=404, detail=f"No data found for ticker '{ticker1}'")
        if not data2:
            raise HTTPException(status_code=404, detail=f"No data found for ticker '{ticker2}'")
        
        return {
            "comparison": f"{ticker1} vs {ticker2}",
            "series1": {
                "ticker": ticker1,
                "title": data1.title,
                "latest_value": data1.data_points[-1].value if data1.data_points else None,
                "latest_date": data1.data_points[-1].date.isoformat() if data1.data_points else None,
                "units": data1.units,
                "data_points": len(data1.data_points)
            },
            "series2": {
                "ticker": ticker2,
                "title": data2.title,
                "latest_value": data2.data_points[-1].value if data2.data_points else None,
                "latest_date": data2.data_points[-1].date.isoformat() if data2.data_points else None,
                "units": data2.units,
                "data_points": len(data2.data_points)
            },
            "comparison_date": datetime.now().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error comparing {ticker1} and {ticker2}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/fred/dashboard")
async def economic_dashboard():
    """Get key economic indicators dashboard"""
    key_indicators = [
        'GDP', 'UNEMPLOYMENT', 'INFLATION', 'FEDFUNDS', 'PAYEMS'
    ]
    
    try:
        # Load all indicators concurrently
        tasks = [
            run_sync_in_thread(fred_loader.load_data, ticker)
            for ticker in key_indicators
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        dashboard = {
            "dashboard_date": datetime.now().isoformat(),
            "indicators": {}
        }
        
        for ticker, result in zip(key_indicators, results):
            if isinstance(result, Exception):
                dashboard["indicators"][ticker] = {
                    "error": str(result),
                    "available": False
                }
            elif result and hasattr(result, 'data_points') and result.data_points:
                latest = result.data_points[-1]
                dashboard["indicators"][ticker] = {
                    "title": result.title,
                    "value": latest.value,
                    "date": latest.date.isoformat(),
                    "units": result.units,
                    "source": result.source,
                    "available": True
                }
            else:
                dashboard["indicators"][ticker] = {
                    "error": "No data available",
                    "available": False
                }
        
        return dashboard
    
    except Exception as e:
        logger.error(f"Error creating dashboard: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/tickers")
async def list_available_tickers():
    """Get list of all available tickers"""
    return {
        "available_tickers": fred_loader.get_available_tickers(),
        "total_count": len(fred_loader.get_available_tickers()),
        "categories": {
            "fred_series": [t for t in fred_loader.get_available_tickers() if not t.endswith('_bls')],
            "bls_fallback": [t for t in fred_loader.get_available_tickers() if t.endswith('_bls')]
        }
    }


@app.post("/refresh/{ticker}")
async def refresh_ticker_data(
    ticker: str,
    background_tasks: BackgroundTasks,
    years_back: int = Query(3, ge=1, le=10)
):
    """Refresh data for a specific ticker in the background"""
    
    def refresh_task(ticker: str, years_back: int):
        """Background task to refresh data"""
        try:
            result = fred_loader.refresh_data(ticker, years_back)
            logger.info(f"Background refresh for {ticker}: {'success' if result else 'failed'}")
        except Exception as e:
            logger.error(f"Background refresh error for {ticker}: {e}")
    
    # Add to background tasks
    background_tasks.add_task(refresh_task, ticker, years_back)
    
    return {
        "message": f"Data refresh initiated for {ticker}",
        "ticker": ticker,
        "years_back": years_back,
        "status": "queued"
    }


@app.get("/cache/stats")
async def get_cache_statistics():
    """Get detailed cache statistics"""
    try:
        stats = mirror_cache.get_cache_stats()
        return {
            "mirror_cache": stats,
            "database_info": {
                "path": fred_loader.db_path,
                "exists": os.path.exists(fred_loader.db_path),
                "size_mb": os.path.getsize(fred_loader.db_path) / (1024*1024) if os.path.exists(fred_loader.db_path) else 0
            },
            "cache_directory": {
                "path": fred_loader.cache_dir,
                "exists": os.path.exists(fred_loader.cache_dir)
            }
        }
    except Exception as e:
        logger.error(f"Error getting cache stats: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.delete("/cache/clear")
async def clear_cache():
    """Clear all cached data"""
    try:
        mirror_cache.clear_cache()
        return {
            "message": "Cache cleared successfully",
            "cleared_at": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        raise HTTPException(status_code=500, detail="Failed to clear cache")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test a simple data load
        test_data = await run_sync_in_thread(fred_loader.load_data, 'GDP')
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "fred_loader": "operational",
                "mirror_cache": "operational", 
                "data_available": test_data is not None
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
        )


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "message": str(exc.detail) if hasattr(exc, 'detail') else "Resource not found",
            "available_endpoints": [
                "/fred/{ticker}",
                "/fred/{ticker}/latest", 
                "/fred/compare/{ticker1}/{ticker2}",
                "/fred/dashboard",
                "/tickers",
                "/cache/stats"
            ]
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 