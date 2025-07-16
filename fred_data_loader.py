"""
FRED Data Loader - Main interface for loading economic data
Provides load_data(ticker, date) function with fallback mechanisms
"""

import os
import json
import sqlite3
import subprocess
import logging
from datetime import datetime, date, timedelta
from typing import Optional, Dict, List, Union, Any
from dataclasses import dataclass
import asyncio

# Import existing BLS client as fallback
try:
    from app.bls_client import BLSClient
except ImportError:
    BLSClient = None


@dataclass
class DataPoint:
    """Data point structure"""
    date: date
    value: float
    period: str
    year: int
    month: int


@dataclass 
class SeriesData:
    """Series data structure"""
    series_id: str
    ticker: str
    title: str
    units: str
    frequency: str
    data_points: List[DataPoint]
    last_updated: str
    source: str = "FRED"


class FREDDataLoader:
    """Main data loader class with multiple data sources"""
    
    def __init__(self, 
                 cache_dir: str = "cached_data",
                 db_path: str = "fred_data.db",
                 enable_scraping: bool = True,
                 enable_bls_fallback: bool = True):
        
        self.cache_dir = cache_dir
        self.db_path = db_path
        self.enable_scraping = enable_scraping
        self.enable_bls_fallback = enable_bls_fallback
        
        self.logger = logging.getLogger(__name__)
        
        # Create directories
        os.makedirs(cache_dir, exist_ok=True)
        
        # Initialize BLS client if available
        self.bls_client = BLSClient() if BLSClient and enable_bls_fallback else None
        
        # Common ticker to FRED series mapping
        self.ticker_mapping = {
            # Popular economic indicators
            'GDP': 'GDP',
            'UNEMPLOYMENT': 'UNRATE', 
            'UNRATE': 'UNRATE',
            'INFLATION': 'CPIAUCSL',
            'CPI': 'CPIAUCSL',
            'CPIAUCSL': 'CPIAUCSL',
            'FEDFUNDS': 'FEDFUNDS',
            'INTEREST_RATE': 'FEDFUNDS',
            'DFF': 'DFF',
            'PAYEMS': 'PAYEMS',
            'JOBS': 'PAYEMS',
            'EMPLOYMENT': 'PAYEMS',
            'HOUSING': 'HOUST',
            'HOUST': 'HOUST',
            'EUR_USD': 'DEXUSEU',
            'USD_JPY': 'DEXJPUS',
            'OIL': 'DCOILWTICO',
            'GOLD': 'GOLDAMGBD228NLBM',
            'SP500': 'SP500',
            'VIX': 'VIXCLS',
            
            # Additional BLS series (fallback)
            'unemployment_bls': 'unemployment',
            'inflation_bls': 'inflation', 
            'jobs_bls': 'jobs',
            'wages': 'wages',
            'productivity': 'productivity'
        }
    
    def load_data(self, 
                  ticker: str, 
                  date_param: Optional[Union[str, date]] = None,
                  years_back: int = 3,
                  force_refresh: bool = False) -> Optional[SeriesData]:
        """
        Main data loading function
        
        Args:
            ticker: Economic indicator ticker/symbol
            date_param: Specific date or None for latest
            years_back: How many years of historical data 
            force_refresh: Force refresh from source
            
        Returns:
            SeriesData object or None if not found
        """
        
        # Normalize ticker
        ticker = ticker.upper()
        series_id = self.ticker_mapping.get(ticker, ticker)
        
        self.logger.info(f"Loading data for {ticker} (series: {series_id})")
        
        # Try different data sources in order of preference
        data = None
        
        # 1. Try cached data first (unless force refresh)
        if not force_refresh:
            data = self._load_from_cache(series_id, date_param)
            if data:
                self.logger.info(f"Loaded {ticker} from cache")
                return data
        
        # 2. Try database
        if not data:
            data = self._load_from_database(series_id, date_param)
            if data:
                self.logger.info(f"Loaded {ticker} from database")
                return data
        
        # 3. Try FRED scraping
        if not data and self.enable_scraping:
            data = self._load_from_scraping(series_id, years_back)
            if data:
                self.logger.info(f"Loaded {ticker} from FRED scraping")
                return data
        
        # 4. Try BLS API fallback
        if not data and self.bls_client and ticker.endswith('_bls'):
            data = self._load_from_bls(ticker.replace('_bls', ''), years_back)
            if data:
                self.logger.info(f"Loaded {ticker} from BLS API")
                return data
        
        self.logger.warning(f"No data found for {ticker}")
        return None
    
    def _load_from_cache(self, series_id: str, date_param: Optional[Union[str, date]]) -> Optional[SeriesData]:
        """Load data from filesystem cache"""
        try:
            cache_file = os.path.join(self.cache_dir, f"{series_id}_latest.json")
            
            if not os.path.exists(cache_file):
                return None
            
            # Check cache age
            file_age = datetime.now() - datetime.fromtimestamp(os.path.getmtime(cache_file))
            if file_age > timedelta(hours=1):  # Cache expires after 1 hour
                return None
            
            with open(cache_file, 'r') as f:
                cached_data = json.load(f)
            
            return self._parse_cached_data(cached_data)
        
        except Exception as e:
            self.logger.error(f"Error loading from cache: {e}")
            return None
    
    def _load_from_database(self, series_id: str, date_param: Optional[Union[str, date]]) -> Optional[SeriesData]:
        """Load data from SQLite database"""
        try:
            if not os.path.exists(self.db_path):
                return None
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get series metadata
            cursor.execute(
                "SELECT * FROM series_metadata WHERE series_id = ?", 
                (series_id,)
            )
            metadata = cursor.fetchone()
            
            if not metadata:
                conn.close()
                return None
            
            # Get data points
            if date_param:
                # Get data up to specific date
                cursor.execute(
                    "SELECT date, value, period, year, month FROM data_points "
                    "WHERE series_id = ? AND date <= ? ORDER BY date",
                    (series_id, str(date_param))
                )
            else:
                # Get all data
                cursor.execute(
                    "SELECT date, value, period, year, month FROM data_points "
                    "WHERE series_id = ? ORDER BY date",
                    (series_id,)
                )
            
            points_data = cursor.fetchall()
            conn.close()
            
            # Convert to DataPoint objects
            data_points = []
            for point in points_data:
                data_points.append(DataPoint(
                    date=datetime.strptime(point[0], '%Y-%m-%d').date(),
                    value=float(point[1]),
                    period=point[2],
                    year=int(point[3]),
                    month=int(point[4])
                ))
            
            return SeriesData(
                series_id=metadata[0],
                ticker=metadata[1] or series_id,
                title=metadata[2] or series_id,
                units=metadata[3] or '',
                frequency=metadata[4] or '',
                data_points=data_points,
                last_updated=metadata[6] or '',
                source="FRED (database)"
            )
        
        except Exception as e:
            self.logger.error(f"Error loading from database: {e}")
            return None
    
    def _load_from_scraping(self, series_id: str, years_back: int) -> Optional[SeriesData]:
        """Load data by running Scrapy spider"""
        try:
            # Run the scrapy spider from the project root with proper python path
            cmd = [
                'scrapy', 'crawl', 'fred',
                '-a', f'series_id={series_id}',
                '-s', 'LOG_LEVEL=WARNING'
            ]
            
            # Set environment variables for proper module resolution
            env = os.environ.copy()
            env['PYTHONPATH'] = os.getcwd()
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60, env=env)
            
            if result.returncode == 0:
                # Try to load the newly scraped data
                return self._load_from_cache(series_id, None)
            else:
                self.logger.error(f"Scrapy failed: {result.stderr}")
            
        except Exception as e:
            self.logger.error(f"Error running scraper: {e}")
        
        return None
    
    def _load_from_bls(self, series_name: str, years_back: int) -> Optional[SeriesData]:
        """Load data from BLS API as fallback"""
        try:
            if not self.bls_client:
                return None
            
            # Run async BLS request
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            bls_data = loop.run_until_complete(
                self.bls_client.get_series_data(series_name, years_back)
            )
            
            loop.close()
            
            # Convert BLS data to our format
            data_points = []
            for point in bls_data.get('data', []):
                try:
                    year = int(point['year'])
                    period = point['period']
                    value = float(point['value'])
                    
                    # Convert period to date
                    if period.startswith('M'):
                        month = int(period[1:])
                        point_date = date(year, month, 1)
                    else:
                        point_date = date(year, 1, 1)
                    
                    data_points.append(DataPoint(
                        date=point_date,
                        value=value,
                        period=f"{year}-{month:02d}" if period.startswith('M') else str(year),
                        year=year,
                        month=month if period.startswith('M') else 1
                    ))
                except (ValueError, KeyError):
                    continue
            
            return SeriesData(
                series_id=bls_data.get('seriesID', series_name),
                ticker=series_name,
                title=bls_data.get('friendly_title', series_name),
                units=bls_data.get('friendly_units', ''),
                frequency='Monthly',
                data_points=sorted(data_points, key=lambda x: x.date),
                last_updated=datetime.now().strftime('%Y-%m-%d'),
                source="BLS API"
            )
        
        except Exception as e:
            self.logger.error(f"Error loading from BLS: {e}")
            return None
    
    def _parse_cached_data(self, cached_data: Dict) -> Optional[SeriesData]:
        """Parse cached JSON data into SeriesData object"""
        try:
            data_points = []
            for point in cached_data.get('data_points', []):
                data_points.append(DataPoint(
                    date=datetime.strptime(point['date'], '%Y-%m-%d').date(),
                    value=float(point['value']),
                    period=point['period'],
                    year=int(point['year']),
                    month=int(point['month'])
                ))
            
            return SeriesData(
                series_id=cached_data['series_id'],
                ticker=cached_data.get('ticker', cached_data['series_id']),
                title=cached_data.get('title', ''),
                units=cached_data.get('units', ''),
                frequency=cached_data.get('frequency', ''),
                data_points=data_points,
                last_updated=cached_data.get('last_updated', ''),
                source="FRED (cached)"
            )
        
        except Exception as e:
            self.logger.error(f"Error parsing cached data: {e}")
            return None
    
    def get_available_tickers(self) -> List[str]:
        """Get list of available tickers"""
        return list(self.ticker_mapping.keys())
    
    def refresh_data(self, ticker: str, years_back: int = 3) -> bool:
        """Force refresh data for a ticker"""
        data = self.load_data(ticker, force_refresh=True, years_back=years_back)
        return data is not None


# Convenience function for easy usage
def load_data(ticker: str, date: Optional[Union[str, date]] = None, years_back: int = 3) -> Optional[SeriesData]:
    """
    Convenience function to load economic data
    
    Usage:
        data = load_data('GDP')
        data = load_data('UNEMPLOYMENT', '2023-12-01')
        data = load_data('CPI', years_back=5)
    """
    loader = FREDDataLoader()
    return loader.load_data(ticker, date, years_back)


# Example usage
if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Example usage
    loader = FREDDataLoader()
    
    # Load unemployment data
    unemployment = load_data('UNEMPLOYMENT')
    if unemployment:
        print(f"Loaded {unemployment.title}")
        print(f"Latest value: {unemployment.data_points[-1].value}% on {unemployment.data_points[-1].date}")
        print(f"Data points: {len(unemployment.data_points)}")
    
    # Load GDP data
    gdp = load_data('GDP')
    if gdp:
        print(f"\nLoaded {gdp.title}")
        print(f"Latest value: {gdp.data_points[-1].value} {gdp.units}")
        print(f"Source: {gdp.source}")
    
    # Show available tickers
    print(f"\nAvailable tickers: {loader.get_available_tickers()[:10]}...")  # Show first 10 