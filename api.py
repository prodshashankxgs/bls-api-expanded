#!/usr/bin/env python3
"""
BLS Data API - FastAPI Web Service
==================================

Platform-agnostic web API for accessing BLS Consumer Price Index data.
Your colleagues can access the data via HTTP requests from any system.

Usage:
    python api.py                    # Start the API server
    uvicorn api:app --reload         # Development mode
    uvicorn api:app --host 0.0.0.0 --port 8000  # Production mode

API Endpoints:
    GET  /                           # API documentation
    GET  /health                     # Health check
    GET  /categories                 # Get available categories
    POST /data                       # Load BLS data
    GET  /data/{categories}/{date}   # Load BLS data (GET method)
    GET  /status                     # Data status information

Author: Generated with Claude Code
Version: 1.0
"""

import os
import sys
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import traceback

from fastapi import FastAPI, HTTPException, Query, Path as PathParam
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
import uvicorn

# Add current directory to Python path for imports
current_dir = Path(__file__).parent.absolute()
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

# Import our BLS components
try:
    from bls_package import get_available_categories, check_setup
    from load_data_enhanced import load_data, load_data_to_dataframe, calculate_inflation_rates
    from config import Config
    from scraper import BLSScraper
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running this from the BLS Scraper API directory")
    sys.exit(1)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="BLS Data API",
    description="Bureau of Labor Statistics Consumer Price Index Data Service",
    version="1.0.0",
    docs_url="/",
    redoc_url="/redoc"
)

# Add CORS middleware for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================================
# PYDANTIC MODELS
# ================================

class DataRequest(BaseModel):
    """Request model for loading BLS data"""
    categories: List[str] = Field(
        ..., 
        description="List of BLS categories to load",
        example=["All items", "Food", "Energy", "Shelter"]
    )
    date: str = Field(
        ..., 
        description="Target date in YYYY-MM format",
        example="2025-06"
    )
    
    @validator('date')
    def validate_date(cls, v):
        try:
            datetime.strptime(v, "%Y-%m")
            return v
        except ValueError:
            raise ValueError("Date must be in YYYY-MM format (e.g., '2025-06')")
    
    @validator('categories')
    def validate_categories(cls, v):
        if not v:
            raise ValueError("At least one category must be specified")
        if len(v) > 20:
            raise ValueError("Maximum 20 categories allowed per request")
        return v

class DataResponse(BaseModel):
    """Response model for BLS data"""
    success: bool
    data: List[Dict[str, Any]]
    message: str
    metadata: Dict[str, Any]

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: str
    data_available: bool
    latest_file: Optional[str]
    categories_count: int

class StatusResponse(BaseModel):
    """Data status response"""
    excel_files_count: int
    latest_file: Optional[str]
    latest_file_date: Optional[str]
    data_directory: str
    cache_directory: str
    available_categories_sample: List[str]

# ================================
# UTILITY FUNCTIONS
# ================================

def ensure_data_available():
    """Ensure BLS data is available, download if needed"""
    try:
        # Check if we have recent data
        latest_file = Config.get_latest_excel_file()
        if latest_file:
            file_age = datetime.now() - datetime.fromtimestamp(latest_file.stat().st_mtime)
            if file_age.total_seconds() < 24 * 3600:  # Less than 24 hours old
                return True
        
        # Try to download new data
        logger.info("Attempting to download latest BLS data...")
        scraper = BLSScraper()
        success = scraper.run_once()
        
        return success
        
    except Exception as e:
        logger.error(f"Error ensuring data availability: {e}")
        return False

def get_api_metadata():
    """Get metadata about the API and data status"""
    try:
        latest_file = Config.get_latest_excel_file()
        categories = get_available_categories(5)  # Sample of 5
        
        return {
            "api_version": "1.0.0",
            "data_source": "Bureau of Labor Statistics",
            "latest_file": latest_file.name if latest_file else None,
            "sample_categories": categories,
            "supported_date_format": "YYYY-MM",
            "max_categories_per_request": 20
        }
    except Exception as e:
        logger.error(f"Error getting metadata: {e}")
        return {"error": str(e)}

# ================================
# API ENDPOINTS
# ================================

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    try:
        # Check if data is available
        data_available = False
        latest_file = None
        categories_count = 0
        
        try:
            latest_file_path = Config.get_latest_excel_file()
            if latest_file_path:
                data_available = True
                latest_file = latest_file_path.name
                categories_count = len(get_available_categories(100))
        except:
            pass
        
        return HealthResponse(
            status="healthy",
            timestamp=datetime.now().isoformat(),
            data_available=data_available,
            latest_file=latest_file,
            categories_count=categories_count
        )
        
    except Exception as e:
        logger.error(f"Health check error: {e}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@app.get("/status", response_model=StatusResponse)
async def get_status():
    """Get detailed status information about available data"""
    try:
        # Get file information
        excel_files = list(Config.DATA_SHEET_DIR.glob("*.xlsx")) if Config.DATA_SHEET_DIR.exists() else []
        latest_file = None
        latest_file_date = None
        
        if excel_files:
            latest_file_path = max(excel_files, key=lambda f: f.stat().st_mtime)
            latest_file = latest_file_path.name
            latest_file_date = datetime.fromtimestamp(latest_file_path.stat().st_mtime).isoformat()
        
        # Get sample categories
        categories_sample = get_available_categories(10)
        
        return StatusResponse(
            excel_files_count=len(excel_files),
            latest_file=latest_file,
            latest_file_date=latest_file_date,
            data_directory=str(Config.DATA_SHEET_DIR),
            cache_directory=str(Config.CACHE_DIR),
            available_categories_sample=categories_sample
        )
        
    except Exception as e:
        logger.error(f"Status error: {e}")
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")

@app.get("/categories")
async def get_categories(limit: int = Query(50, description="Maximum number of categories to return")):
    """Get available BLS categories"""
    try:
        # Ensure data is available
        if not ensure_data_available():
            raise HTTPException(status_code=503, detail="BLS data not available. Please try again later.")
        
        categories = get_available_categories(min(limit, 100))  # Cap at 100
        
        return {
            "success": True,
            "categories": categories,
            "count": len(categories),
            "message": f"Retrieved {len(categories)} available categories"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Categories error: {e}")
        raise HTTPException(status_code=500, detail=f"Error retrieving categories: {str(e)}")

@app.post("/data", response_model=DataResponse)
async def load_bls_data(request: DataRequest):
    """Load BLS data for specified categories and date"""
    try:
        logger.info(f"Loading data for {len(request.categories)} categories, date: {request.date}")
        
        # Ensure data is available
        if not ensure_data_available():
            raise HTTPException(status_code=503, detail="BLS data not available. Please try again later.")
        
        # Load the data
        data = load_data(request.categories, request.date)
        
        if not data:
            return DataResponse(
                success=False,
                data=[],
                message=f"No data found for the specified categories and date {request.date}",
                metadata=get_api_metadata()
            )
        
        # Calculate some summary statistics
        successful_categories = len(data)
        failed_categories = len(request.categories) - successful_categories
        
        return DataResponse(
            success=True,
            data=data,
            message=f"Successfully loaded data for {successful_categories} categories",
            metadata={
                **get_api_metadata(),
                "requested_categories": len(request.categories),
                "successful_categories": successful_categories,
                "failed_categories": failed_categories,
                "request_date": request.date
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Data loading error: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error loading data: {str(e)}")

@app.get("/data/{categories}/{date}")
async def load_bls_data_get(
    categories: str = PathParam(..., description="Comma-separated list of categories"),
    date: str = PathParam(..., description="Date in YYYY-MM format")
):
    """Load BLS data via GET request (alternative to POST)"""
    try:
        # Parse categories
        category_list = [cat.strip() for cat in categories.split(",") if cat.strip()]
        
        if not category_list:
            raise HTTPException(status_code=400, detail="At least one category must be specified")
        
        if len(category_list) > 20:
            raise HTTPException(status_code=400, detail="Maximum 20 categories allowed per request")
        
        # Validate date format
        try:
            datetime.strptime(date, "%Y-%m")
        except ValueError:
            raise HTTPException(status_code=400, detail="Date must be in YYYY-MM format")
        
        # Create request object and process
        request = DataRequest(categories=category_list, date=date)
        return await load_bls_data(request)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"GET data loading error: {e}")
        raise HTTPException(status_code=500, detail=f"Error loading data: {str(e)}")

@app.get("/download")
async def download_latest_data():
    """Download the latest BLS data files"""
    try:
        logger.info("Manual data download requested")
        
        scraper = BLSScraper()
        success = scraper.run_once()
        
        if success:
            latest_file = Config.get_latest_excel_file()
            return {
                "success": True,
                "message": "Successfully downloaded latest BLS data",
                "latest_file": latest_file.name if latest_file else None,
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "success": False,
                "message": "No new data available or download failed",
                "timestamp": datetime.now().isoformat()
            }
            
    except Exception as e:
        logger.error(f"Download error: {e}")
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")

# ================================
# STARTUP EVENT
# ================================

@app.on_event("startup")
async def startup_event():
    """Initialize the API on startup"""
    logger.info("🏛️  Starting BLS Data API...")
    
    try:
        # Ensure directories exist
        Config.ensure_directories_exist()
        
        # Check if we have data, download if needed
        ensure_data_available()
        
        logger.info("✅ BLS Data API startup complete")
        
    except Exception as e:
        logger.error(f"❌ Startup error: {e}")

# ================================
# MAIN FUNCTION
# ================================

def main():
    """Main function to run the API server"""
    print("🏛️  BLS Data API Server")
    print("=" * 50)
    print("Bureau of Labor Statistics Data Service")
    print()
    
    # Configuration info
    print(f"📁 Data Directory: {Config.DATA_SHEET_DIR}")
    print(f"📁 Cache Directory: {Config.CACHE_DIR}")
    print(f"🌐 API Host: {Config.API_HOST}")
    print(f"🔌 API Port: {Config.API_PORT}")
    print()
    
    # Check setup
    print("🔍 Checking setup...")
    try:
        if check_setup():
            print("✅ Setup check passed")
        else:
            print("⚠️  Setup check failed, but continuing...")
    except Exception as e:
        print(f"⚠️  Setup check error: {e}")
    
    print()
    print("🚀 Starting API server...")
    print(f"📖 API Documentation: http://{Config.API_HOST}:{Config.API_PORT}/")
    print(f"🏥 Health Check: http://{Config.API_HOST}:{Config.API_PORT}/health")
    print()
    print("Press Ctrl+C to stop the server")
    print("=" * 50)
    
    # Run the server
    uvicorn.run(
        "api:app",
        host=Config.API_HOST,
        port=Config.API_PORT,
        reload=Config.API_RELOAD
    )

if __name__ == "__main__":
    main()