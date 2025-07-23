#!/usr/bin/env python3
"""
bls economic data api - all-in-one production server
complete fastapi application with built-in bls scraping, caching, and optimization
"""

import os
import sys
import json
import time
import pickle
import hashlib
import random
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from contextlib import asynccontextmanager
from concurrent.futures import ThreadPoolExecutor

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import pandas as pd

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn
from dotenv import load_dotenv

load_dotenv()

# configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('bls_api.log', mode='a')
    ]
)
logger = logging.getLogger(__name__)

# configuration
API_VERSION = "2.0.0"
MAX_RESULTS = int(os.getenv('MAX_RESULTS', 1000))
CACHE_DIR = Path(os.getenv('DATA_CACHE_DIR', 'data_cache'))
CACHE_TTL = int(os.getenv('CACHE_TTL', 3600))
CACHE_DIR.mkdir(exist_ok=True)

# bls data scraper (built-in)

class BLSScraper:
    """high-performance bls data scraper with caching"""
    
    def __init__(self):
        self.cache_dir = CACHE_DIR
        self.cache_hours = 1
        
        # economic indicator mappings with categories - BLS timeseries IDs
        self.series_map = {
            'cpi': {'series_id': 'CUUR0000SA0', 'category': 'Consumer Price Index', 'timeseries': True},
            'cpi_all': {'series_id': 'CUUR0000SA0', 'category': 'Consumer Price Index', 'timeseries': True},
            'cpi_core': {'series_id': 'CUUR0000SA0L1E', 'category': 'Core CPI (Less Food and Energy)', 'timeseries': True}, 
            'cpi_food': {'series_id': 'CUUR0000SAF1', 'category': 'Food Consumer Price Index', 'timeseries': True},
            'cpi_energy': {'series_id': 'CUUR0000SA0E', 'category': 'Energy Consumer Price Index', 'timeseries': True},
            'cpi_housing': {'series_id': 'CUUR0000SAH1', 'category': 'Housing Consumer Price Index', 'timeseries': True},
            'ppi': {'series_id': 'WPUFD49207', 'category': 'Producer Price Index', 'timeseries': True},
            'ppi_all': {'series_id': 'WPUFD4', 'category': 'Producer Price Index (All Commodities)', 'timeseries': True},
            'unemployment': {'series_id': 'LNS14000000', 'category': 'Unemployment Rate', 'timeseries': True},
            'gdp': {'series_id': 'GDP', 'category': 'Gross Domestic Product', 'timeseries': False}  # GDP not available in timeseries
        }
        
        # data sources
        self.data_sources = {
            'bls_api': 'https://api.bls.gov/publicAPI/v2/timeseries/data/',
            'bls_cpi': 'https://www.bls.gov/news.release/cpi.nr0.htm',
            'bls_ppi': 'https://www.bls.gov/news.release/ppi.nr0.htm',
            'bls_timeseries': 'https://data.bls.gov/timeseries/'
        }
        
        self.session = self._create_session()
        
    def _create_session(self) -> requests.Session:
        """create optimized requests session"""
        session = requests.Session()
        
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        user_agents = [
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        ]
        
        session.headers.update({
            'User-Agent': random.choice(user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive'
        })
        
        return session
    
    def _get_cache_file(self, ticker: str, date_range: str) -> Path:
        """generate cache file path"""
        cache_key = f"{ticker}_{date_range or 'default'}"
        filename = hashlib.md5(cache_key.encode()).hexdigest() + '.json'
        return self.cache_dir / filename
    
    def _is_cache_valid(self, cache_file: Path) -> bool:
        """check if cache file is still valid"""
        if not cache_file.exists():
            return False
        
        cache_age = time.time() - cache_file.stat().st_mtime
        return cache_age < (self.cache_hours * 3600)
    
    def _load_from_cache(self, ticker: str, date_range: str) -> Optional[List[Dict]]:
        """load data from cache if valid"""
        cache_file = self._get_cache_file(ticker, date_range)
        
        if self._is_cache_valid(cache_file):
            try:
                with open(cache_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"cache read error: {e}")
                
        return None
    
    def _save_to_cache(self, ticker: str, date_range: str, data: List[Dict]):
        """save data to cache"""
        if not data:
            return
            
        cache_file = self._get_cache_file(ticker, date_range)
        
        try:
            with open(cache_file, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            logger.error(f"cache write error: {e}")
    
    def _parse_date_range(self, date_str: str) -> tuple:
        """parse date range string - defaults to 2015-01 to 2025-06"""
        if not date_str:
            # Default to 2015 to min(current year, 2025) based on datetime
            current_date = datetime.now()
            target_end = datetime(2025, 6, 1)  # 2025-06
            
            # Use the earlier of current date or 2025-06
            if current_date > target_end:
                end_year = target_end.year
            else:
                end_year = current_date.year
            
            return 2015, end_year
        
        date_str = date_str.lower().strip()
        current_year = datetime.now().year
        
        # handle various formats
        if 'last' in date_str and 'year' in date_str:
            years = int(''.join(filter(str.isdigit, date_str)) or '3')
            return current_year - years, current_year
        elif '-' in date_str:
            parts = date_str.split('-')
            start_year = int(parts[0])
            end_year = int(parts[1]) if len(parts) > 1 else current_year
            return start_year, end_year
        elif date_str.isdigit():
            year = int(date_str)
            return year, year
        else:
            # Default range: 2015 to 2025
            return 2015, 2025
    
    def _scrape_bls_data(self, ticker: str, start_year: int, end_year: int) -> List[Dict]:
        """scrape data from bls sources"""
        data = []
        
        try:
            # try bls api first
            series_info = self.series_map.get(ticker)
            if series_info:
                api_data = self._try_bls_api(ticker, series_info, start_year, end_year)
                if api_data:
                    data.extend(api_data)
            
            # fallback to web scraping if needed
            if not data:
                web_data = self._try_web_scraping(ticker)
                if web_data:
                    data.extend(web_data)
            
        except Exception as e:
            logger.error(f"scraping error for {ticker}: {e}")
        
        return data
    
    def _try_bls_api(self, ticker: str, series_info: dict, start_year: int, end_year: int) -> List[Dict]:
        """try bls official api"""
        try:
            series_id = series_info['series_id']
            category = series_info['category']
            
            payload = {
                'seriesid': [series_id],
                'startyear': str(start_year),
                'endyear': str(end_year)
            }
            
            response = self.session.post(
                self.data_sources['bls_api'],
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('status') == 'REQUEST_SUCCEEDED':
                    series_data = result['Results']['series'][0]['data']
                    
                    return [
                        {
                            'ticker': ticker,
                            'year': int(item['year']),
                            'month': int(item['period'][1:]) if item['period'].startswith('M') else int(item['period'][1:]),
                            'value': float(item['value']),
                            'series_id': series_id,
                            'category': category,
                            'source': 'bls api'
                        }
                        for item in series_data
                        if item['value'] not in ['.', '', None]
                    ]
        except Exception as e:
            logger.debug(f"bls api error: {e}")
        
        return []
    
    def _try_web_scraping(self, ticker: str) -> List[Dict]:
        """fallback web scraping using BLS timeseries"""
        try:
            series_info = self.series_map.get(ticker)
            if series_info and series_info.get('timeseries', False):
                # Use the general timeseries scraper for all supported indicators
                return self.scrape_bls_timeseries(
                    series_info['series_id'], 
                    ticker, 
                    series_info['category']
                )
            elif ticker == 'ppi':  
                return self._scrape_ppi_web()
        except Exception as e:
            logger.debug(f"web scraping error for {ticker}: {e}")
        
        return []
    
    def _scrape_cpi_web(self) -> List[Dict]:
        """scrape cpi from bls website"""
        try:
            response = self.session.get(self.data_sources['bls_cpi'], timeout=30)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # look for cpi data in tables
            tables = soup.find_all('table')
            data = []
            
            for table in tables:
                rows = table.find_all('tr')
                for row in rows[1:]:  # skip header
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        try:
                            date_text = cells[0].get_text().strip()
                            value_text = cells[1].get_text().strip()
                            
                            # parse date and value
                            if date_text and value_text and value_text.replace('.', '').isdigit():
                                value = float(value_text)
                                
                                # simple date parsing
                                current_year = datetime.now().year
                                data.append({
                                    'date': f"{current_year}-01-01",
                                    'value': value,
                                    'year': current_year,
                                    'source': 'bls web'
                                })
                        except:
                            continue
                            
            return data[:20]  # return recent data
            
        except Exception as e:
            logger.debug(f"cpi web scraping error: {e}")
            
        return []
    
    def _scrape_cpi_timeseries(self) -> List[Dict]:
        """scrape cpi data from bls timeseries table"""
        try:
            url = "https://data.bls.gov/timeseries/CUUR0000SA0?years_option=all_years"
            response = self.session.get(url, timeout=30)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            data = []
            
            # Find the main data table - BLS uses specific table structure
            table = soup.find('table', {'class': 'regular-data'})
            if not table:
                # Try alternative table selectors
                table = soup.find('table', {'id': 'table0'}) or soup.find('table')
            
            if table:
                rows = table.find_all('tr')
                
                # Find header row to identify month columns
                header_row = None
                for i, row in enumerate(rows):
                    if row.find('th'):
                        header_row = row
                        break
                
                if header_row:
                    headers = [th.get_text().strip() for th in header_row.find_all('th')]
                    
                    # Process data rows
                    for row in rows[1:]:  # Skip header
                        cells = row.find_all(['td', 'th'])
                        if len(cells) >= 2:
                            try:
                                year_text = cells[0].get_text().strip()
                                
                                # Validate year
                                if year_text.isdigit() and len(year_text) == 4:
                                    year = int(year_text)
                                    
                                    # Process monthly data
                                    for i, cell in enumerate(cells[1:], 1):
                                        if i < len(headers):
                                            value_text = cell.get_text().strip()
                                            
                                            # Skip if no value or placeholder
                                            if value_text in ['', '-', '.', 'M']:
                                                continue
                                            
                                            try:
                                                value = float(value_text)
                                                month_name = headers[i].lower()
                                                
                                                # Map month names to numbers
                                                month_map = {
                                                    'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4,
                                                    'may': 5, 'jun': 6, 'jul': 7, 'aug': 8,
                                                    'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
                                                }
                                                
                                                month = month_map.get(month_name[:3], None)
                                                if month:
                                                    data.append({
                                                        'ticker': 'cpi',
                                                        'year': year,
                                                        'month': month,
                                                        'value': value,
                                                        'series_id': 'CUUR0000SA0',
                                                        'category': 'Consumer Price Index',
                                                        'source': 'bls timeseries'
                                                    })
                                            except ValueError:
                                                continue
                            except ValueError:
                                continue
            
            # Sort by year and month (most recent first)
            data.sort(key=lambda x: (x['year'], x['month']), reverse=True)
            
            logger.info(f"Scraped {len(data)} CPI data points from BLS timeseries")
            return data
            
        except Exception as e:
            logger.error(f"CPI timeseries scraping error: {e}")
            return []
    
    def scrape_bls_timeseries(self, series_id: str, ticker: str = None, category: str = None) -> List[Dict]:
        """scrape data from any BLS timeseries URL"""
        try:
            url = f"{self.data_sources['bls_timeseries']}{series_id}?years_option=all_years"
            response = self.session.get(url, timeout=30)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            data = []
            
            # Find the main data table - BLS uses specific table structure
            table = soup.find('table', {'class': 'regular-data'})
            if not table:
                # Try alternative table selectors
                table = soup.find('table', {'id': 'table0'}) or soup.find('table')
            
            if table:
                rows = table.find_all('tr')
                
                # Find header row to identify month columns
                header_row = None
                for i, row in enumerate(rows):
                    if row.find('th'):
                        header_row = row
                        break
                
                if header_row:
                    headers = [th.get_text().strip() for th in header_row.find_all('th')]
                    
                    # Process data rows
                    for row in rows[1:]:  # Skip header
                        cells = row.find_all(['td', 'th'])
                        if len(cells) >= 2:
                            try:
                                year_text = cells[0].get_text().strip()
                                
                                # Validate year
                                if year_text.isdigit() and len(year_text) == 4:
                                    year = int(year_text)
                                    
                                    # Process monthly data
                                    for i, cell in enumerate(cells[1:], 1):
                                        if i < len(headers):
                                            value_text = cell.get_text().strip()
                                            
                                            # Skip if no value or placeholder
                                            if value_text in ['', '-', '.', 'M']:
                                                continue
                                            
                                            try:
                                                value = float(value_text)
                                                month_name = headers[i].lower()
                                                
                                                # Map month names to numbers
                                                month_map = {
                                                    'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4,
                                                    'may': 5, 'jun': 6, 'jul': 7, 'aug': 8,
                                                    'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
                                                }
                                                
                                                month = month_map.get(month_name[:3], None)
                                                if month:
                                                    data.append({
                                                        'ticker': ticker or series_id.lower(),
                                                        'year': year,
                                                        'month': month,
                                                        'value': value,
                                                        'series_id': series_id,
                                                        'category': category or f'Series {series_id}',
                                                        'source': 'bls timeseries'
                                                    })
                                            except ValueError:
                                                continue
                            except ValueError:
                                continue
            
            # Sort by year and month (most recent first)
            data.sort(key=lambda x: (x['year'], x['month']), reverse=True)
            
            logger.info(f"Scraped {len(data)} data points from BLS timeseries {series_id}")
            return data
            
        except Exception as e:
            logger.error(f"BLS timeseries scraping error for {series_id}: {e}")
            return []
    
    def _scrape_ppi_web(self) -> List[Dict]:
        """scrape ppi from bls website"""
        # similar implementation to cpi scraping
        return []
    
    def load_data(self, ticker: str, date_range: str = None) -> List[Dict]:
        """main data loading function - returns data as list of dictionaries"""
        ticker = ticker.lower().strip()
        
        # check cache first
        cached_data = self._load_from_cache(ticker, date_range)
        if cached_data:
            return cached_data
        
        # parse date range
        start_year, end_year = self._parse_date_range(date_range)
        
        # scrape fresh data
        data = self._scrape_bls_data(ticker, start_year, end_year)
        
        # sort by year and month (most recent first)
        data.sort(key=lambda x: (x.get('year', 0), x.get('month', 0)), reverse=True)
        
        # cache the result
        self._save_to_cache(ticker, date_range, data)
        
        return data
    
    def load_dataframe(self, ticker: str, date_range: str = None) -> pd.DataFrame:
        """load data and return as pandas DataFrame with specified columns"""
        data = self.load_data(ticker, date_range)
        
        if not data:
            # Return empty DataFrame with correct columns
            return pd.DataFrame(columns=['ticker', 'year', 'month', 'value', 'series_id', 'category'])
        
        # Create DataFrame from the data
        df = pd.DataFrame(data)
        
        # Ensure we have all required columns
        required_columns = ['ticker', 'year', 'month', 'value', 'series_id', 'category']
        for col in required_columns:
            if col not in df.columns:
                df[col] = None
        
        # Select and reorder columns
        df = df[required_columns]
        
        # Sort by year and month (most recent first)
        df = df.sort_values(['year', 'month'], ascending=[False, False]).reset_index(drop=True)
        
        return df
    
    def get_available_indicators(self) -> Dict[str, str]:
        """Get available economic indicators"""
        return {
            'cpi': 'Consumer Price Index (All Items)',
            'cpi_core': 'Core CPI (Less Food and Energy)',
            'cpi_food': 'Food Consumer Price Index',
            'cpi_energy': 'Energy Consumer Price Index',
            'cpi_housing': 'Housing Consumer Price Index',
            'ppi': 'Producer Price Index',
            'unemployment': 'Unemployment Rate',
            'gdp': 'Gross Domestic Product'
        }
    
    def clear_cache(self):
        """Clear all cached data"""
        try:
            for cache_file in self.cache_dir.glob('*.json'):
                cache_file.unlink()
            logger.info("Cache cleared")
        except Exception as e:
            logger.error(f"Cache clear error: {e}")

# ============================================================================
# CACHING SYSTEM
# ============================================================================

class SimpleCache:
    """Lightweight in-memory cache with file persistence"""
    
    def __init__(self):
        self.memory_cache = {}
        self.cache_dir = CACHE_DIR
        self.ttl = CACHE_TTL
        
    def _key(self, ticker: str, date: Optional[str] = None) -> str:
        key_str = f"{ticker}_{date or 'default'}"
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def get(self, ticker: str, date: Optional[str] = None) -> Optional[Any]:
        cache_key = self._key(ticker, date)
        current_time = time.time()
        
        # Check memory cache
        if cache_key in self.memory_cache:
            data, timestamp = self.memory_cache[cache_key]
            if current_time - timestamp < self.ttl:
                return data
            else:
                del self.memory_cache[cache_key]
        
        # Check file cache
        cache_file = self.cache_dir / f"{cache_key}.pkl"
        if cache_file.exists():
            try:
                with open(cache_file, 'rb') as f:
                    data, timestamp = pickle.load(f)
                
                if current_time - timestamp < self.ttl:
                    self.memory_cache[cache_key] = (data, timestamp)
                    return data
                else:
                    cache_file.unlink()
            except Exception as e:
                logger.error(f"cache read error: {e}")
                if cache_file.exists():
                    cache_file.unlink()
        
        return None
    
    def set(self, ticker: str, data: Any, date: Optional[str] = None):
        if not data:
            return
            
        cache_key = self._key(ticker, date)
        timestamp = time.time()
        
        # Store in memory
        self.memory_cache[cache_key] = (data, timestamp)
        
        # Store in file
        try:
            cache_file = self.cache_dir / f"{cache_key}.pkl"
            with open(cache_file, 'wb') as f:
                pickle.dump((data, timestamp), f)
        except Exception as e:
            logger.error(f"cache write error: {e}")
    
    def clear(self):
        self.memory_cache.clear()
        try:
            for cache_file in self.cache_dir.glob("*.pkl"):
                cache_file.unlink()
            for cache_file in self.cache_dir.glob("*.json"):
                cache_file.unlink()
        except Exception as e:
            logger.error(f"Cache clear error: {e}")

# Global instances
scraper = BLSScraper()
cache = SimpleCache()
executor = ThreadPoolExecutor(max_workers=4)

class OptimizedScraper:
    """High-performance scraper with caching"""
    
    def __init__(self):
        self.cache_hits = 0
        self.cache_misses = 0
        self.total_requests = 0
    
    def load_data(self, ticker: str, date_range: Optional[str] = None) -> List[Dict]:
        self.total_requests += 1
        
        # Try cache first
        cached = cache.get(ticker, date_range)
        if cached is not None:
            self.cache_hits += 1
            return cached
        
        # Cache miss - fetch data
        self.cache_misses += 1
        try:
            data = scraper.load_data(ticker, date_range)
            if data:
                cache.set(ticker, data, date_range)
            return data or []
        except Exception as e:
            logger.error(f"Data loading error for {ticker}: {e}")
            return []
    
    def get_stats(self) -> Dict[str, Any]:
        hit_rate = self.cache_hits / max(self.total_requests, 1)
        return {
            "total_requests": self.total_requests,
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "hit_rate": f"{hit_rate:.1%}"
        }

optimized_scraper = OptimizedScraper()

# ============================================================================
# FASTAPI APPLICATION
# ============================================================================

# Pydantic models
class DataResponse(BaseModel):
    status: str
    timestamp: str
    ticker: str
    date_range: str
    count: int
    data: List[Dict]

class ErrorResponse(BaseModel):
    error: str
    status: str = Field(default="error")
    timestamp: str

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup/shutdown handling"""
    logger.info(f"Starting BLS Scraper API v{API_VERSION}")
    
    # Warmup cache with common data
    try:
        common_tickers = ['cpi', 'cpi_core', 'ppi', 'unemployment']
        for ticker in common_tickers:
            try:
                optimized_scraper.load_data(ticker, '2024')
                logger.info(f"Warmed up {ticker}")
            except:
                pass
        logger.info("Cache warmup complete")
    except Exception as e:
        logger.error(f"Warmup failed: {e}")
    
    yield
    
    logger.info("Shutting down API")
    executor.shutdown(wait=True)

# FastAPI app
app = FastAPI(
    title="BLS Economic Data API",
    description="""
    High-performance API for US Bureau of Labor Statistics economic data.
    
    ## Quick Usage
    * Get CPI data: `/data/cpi?date=2022-2024`
    * Get unemployment: `/data/unemployment?date=2023`
    * Get available indicators: `/indicators`
    
    ## Features
    * Intelligent caching for fast responses
    * Multiple output formats (JSON/CSV)
    * Concurrent request handling
    * Automatic API documentation
    """,
    version=API_VERSION,
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    logger.error(f"HTTP {exc.status_code}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.detail,
            timestamp=datetime.now().isoformat()
        ).dict()
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unexpected error: {exc}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal server error",
            timestamp=datetime.now().isoformat()
        ).dict()
    )

# Routes
@app.get("/")
async def root():
    """API information"""
    return {
        "name": "BLS Economic Data API",
        "version": API_VERSION,
        "description": "Fast, reliable economic data from the Bureau of Labor Statistics",
        "status": "active",
        "timestamp": datetime.now().isoformat(),
        "documentation": "/docs",
        "endpoints": {
            "GET /": "API information",
            "GET /health": "Health check",
            "GET /indicators": "Available indicators",
            "GET /data/{ticker}": "Get economic data",
            "GET /stats": "Performance statistics",
            "POST /clear-cache": "Clear cache"
        },
        "examples": {
            "cpi_data": "/data/cpi?date=2022-2024",
            "unemployment": "/data/unemployment?date=2023",
            "csv_export": "/data/cpi?format=csv"
        }
    }

@app.get("/health")
async def health_check():
    """Health check"""
    try:
        test_data = optimized_scraper.load_data('cpi', '2024')
        is_healthy = len(test_data) > 0
        
        return {
            "status": "healthy" if is_healthy else "degraded",
            "timestamp": datetime.now().isoformat(),
            "version": API_VERSION,
            "data_available": is_healthy,
            "cache_directory_exists": CACHE_DIR.exists()
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

@app.get("/indicators")
async def get_indicators():
    """Get available economic indicators"""
    try:
        indicators = scraper.get_available_indicators()
        return {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "indicators": indicators,
            "count": len(indicators)
        }
    except Exception as e:
        logger.error(f"Failed to get indicators: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve indicators")

@app.get("/data/{ticker}")
async def get_economic_data(
    ticker: str,
    date: Optional[str] = None,
    format: str = "json",
    limit: Optional[int] = None
):
    """Get economic data for specified indicator"""
    
    if not ticker.strip():
        raise HTTPException(status_code=400, detail="Ticker parameter is required")
    
    ticker = ticker.strip().lower()
    
    # Validate format parameter
    if format not in ["json", "csv"]:
        raise HTTPException(status_code=400, detail="Format must be 'json' or 'csv'")
    
    try:
        data = optimized_scraper.load_data(ticker, date)
        
        if not data:
            raise HTTPException(
                status_code=404,
                detail=f"No data found for ticker '{ticker}' with date range '{date}'"
            )
        
        # Apply limit
        if limit and len(data) > limit:
            data = data[:limit]
        elif len(data) > MAX_RESULTS:
            data = data[:MAX_RESULTS]
        
        # Handle CSV format
        if format == "csv":
            import io
            import csv
            
            output = io.StringIO()
            if data:
                writer = csv.DictWriter(output, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
            
            return StreamingResponse(
                io.BytesIO(output.getvalue().encode()),
                media_type="text/csv",
                headers={"Content-Disposition": f"attachment; filename={ticker}_data.csv"}
            )
        
        return {
            "status": "success",
            "timestamp": datetime.now().isoformat(),
            "ticker": ticker,
            "date_range": date or "default",
            "count": len(data),
            "data": data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get data for {ticker}: {e}")
        raise HTTPException(status_code=500, detail=f"Data retrieval failed: {str(e)}")

@app.get("/stats")
async def get_stats():
    """Get API performance statistics"""
    return {
        "status": "success",
        "timestamp": datetime.now().isoformat(),
        "stats": optimized_scraper.get_stats()
    }

@app.post("/clear-cache")
async def clear_cache_endpoint():
    """Clear all cached data"""
    try:
        cache.clear()
        scraper.clear_cache()
        logger.info("Cache cleared")
        return {
            "status": "success",
            "message": "Cache cleared successfully",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to clear cache: {e}")
        raise HTTPException(status_code=500, detail="Failed to clear cache")

def main():
    """Main entry point"""
    port = int(os.getenv('PORT', 8000))
    host = os.getenv('HOST', '0.0.0.0')
    workers = int(os.getenv('WORKERS', 1))
    reload = os.getenv('RELOAD', 'false').lower() == 'true'
    
    logger.info(f"Starting BLS API on {host}:{port}")
    logger.info(f"Documentation: http://{host}:{port}/docs")
    
    uvicorn.run(
        "bls_api:app",
        host=host,
        port=port,
        workers=workers,
        reload=reload,
        log_level="info"
    )

if __name__ == '__main__':
    main()