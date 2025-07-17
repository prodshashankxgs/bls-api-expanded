import json
import os
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from typing import Dict, List, Optional, Tuple, Union
import glob
from dataclasses import dataclass

# Import the new standardized schema
from .standardized_schema import (
    standardize_data, DataSource, StandardizedDataFormatter
)

@dataclass
class BLSDataPoint:
    """Simple data structure for BLS data points"""
    series_id: str
    date: str
    value: float
    period: str
    year: int
    month: Optional[int] = None
    
class FastBLSAPI:
    """High-performance BLS data API using cached data"""
    
    def __init__(self, cache_dir: str = "cached_data", max_workers: int = 10):
        self.cache_dir = cache_dir
        self.max_workers = max_workers
        self.formatter = StandardizedDataFormatter()
        
        # Common series mappings
        self.series_map = {
            'cpi': 'CPIAUCSL',
            'cpi_all': 'CPIAUCSL', 
            'cpi_core': 'CPILFESL',
            'cpi_food': 'CPIUFDSL',
            'cpi_energy': 'CPIENGSL',
            'cpi_housing': 'CPIHOSSL',
            'ppi': 'PPIFIS',
            'ppi_all': 'PPIFIS',
            'ppi_core': 'PPIFCG',
            'ppi_energy': 'PPIENG',
            'ppi_aco': 'PPIACO',
            'unemployment': 'UNRATE',
            'gdp': 'GDP'
        }
        
        # Cache for loaded data
        self._data_cache = {}
        
    def _get_latest_cache_file(self, series_id: str) -> Optional[str]:
        """Find the latest cache file for a series"""
        # First try _latest.json
        latest_file = os.path.join(self.cache_dir, f"{series_id}_latest.json")
        if os.path.exists(latest_file):
            return latest_file
        
        # Then try timestamped files
        pattern = os.path.join(self.cache_dir, f"{series_id}_*.json")
        files = glob.glob(pattern)
        
        if not files:
            return None
        
        # Return the most recent file
        return max(files, key=os.path.getmtime)
        
    def _load_series_from_cache(self, series_id: str) -> List[BLSDataPoint]:
        """Load data for a series from cache"""
        # Check memory cache first
        if series_id in self._data_cache:
            return self._data_cache[series_id]
        
        cache_file = self._get_latest_cache_file(series_id)
        if not cache_file:
            print(f"No cached data found for {series_id}")
            return []
        
        try:
            with open(cache_file, 'r') as f:
                data = json.load(f)
            
            data_points = []
            if 'data_points' in data:
                for point in data['data_points']:
                    try:
                        data_points.append(BLSDataPoint(
                            series_id=series_id,
                            date=point['date'],
                            value=float(point['value']),
                            period=point['period'],
                            year=int(point['year']),
                            month=point.get('month')
                        ))
                    except (ValueError, KeyError) as e:
                        continue
            
            # Cache in memory
            self._data_cache[series_id] = data_points
            
            print(f"Loaded {len(data_points)} data points for {series_id} from cache")
            return data_points
            
        except Exception as e:
            print(f"Error loading cached data for {series_id}: {e}")
            return []
    
    def _normalize_series_id(self, ticker: str) -> str:
        """Normalize ticker to BLS series ID"""
        ticker_lower = ticker.lower().strip()
        
        # Check if it's already a BLS series ID
        if ticker_lower.startswith(('cpi', 'ppi', 'unrate', 'gdp')) and len(ticker) > 6:
            return ticker.upper()
        
        # Map common names
        return self.series_map.get(ticker_lower, ticker.upper())
    
    def _parse_date_range(self, date_input: Optional[str] = None) -> Tuple[int, int]:
        """Parse date input and return start_year, end_year"""
        current_year = datetime.now().year
        
        if not date_input:
            # Default: last 3 years
            return current_year - 2, current_year
        
        date_input = date_input.strip()
        
        # Handle year ranges like "2020-2023" or "2020:2023"
        if '-' in date_input or ':' in date_input:
            separator = '-' if '-' in date_input else ':'
            parts = date_input.split(separator)
            if len(parts) == 2:
                try:
                    start_year = int(parts[0].strip())
                    end_year = int(parts[1].strip())
                    return start_year, end_year
                except ValueError:
                    pass
        
        # Handle single year
        try:
            year = int(date_input)
            return year, year
        except ValueError:
            pass
        
        # Handle "last X years"
        if 'last' in date_input.lower() and 'year' in date_input.lower():
            import re
            numbers = re.findall(r'\d+', date_input)
            if numbers:
                years_back = int(numbers[0])
                return current_year - years_back, current_year
        
        # Default fallback
        print(f"Could not parse date '{date_input}', using last 3 years")
        return current_year - 2, current_year
    
    def _filter_by_date_range(self, data_points: List[BLSDataPoint], start_year: int, end_year: int) -> List[BLSDataPoint]:
        """Filter data points by year range"""
        return [dp for dp in data_points if start_year <= dp.year <= end_year]
    
    def load_data(self, ticker: str, date: Optional[str] = None, standardized: bool = True) -> Union[List[Dict], Dict]:
        """
        Load BLS data for given ticker and date range
        
        Args:
            ticker: CPI/PPI ticker (e.g., 'cpi', 'ppi', 'cpi_core', 'CPIAUCSL')
            date: Date range (e.g., '2023', '2020-2023', 'last 3 years') or None for last 3 years
            standardized: Whether to return standardized professional format
            
        Returns:
            Standardized professional response dict or legacy list of dictionaries
        """
        start_time = time.time()
        
        # Normalize inputs
        series_id = self._normalize_series_id(ticker)
        start_year, end_year = self._parse_date_range(date)
        
        print(f"Loading {series_id} data for {start_year}-{end_year}...")
        
        try:
            # Load from cache
            all_data = self._load_series_from_cache(series_id)
            
            # Filter by date range
            filtered_data = self._filter_by_date_range(all_data, start_year, end_year)
            
            # Convert to dictionaries and sort by date
            result = []
            for dp in filtered_data:
                result.append({
                    'series_id': dp.series_id,
                    'date': dp.date,
                    'value': dp.value,
                    'period': dp.period,
                    'year': dp.year,
                    'month': dp.month
                })
            
            # Sort by year and month (most recent first)
            result.sort(key=lambda x: (x['year'], x['month'] or 0), reverse=True)
            
            elapsed = time.time() - start_time
            print(f"✅ Loaded {len(result)} data points in {elapsed:.2f} seconds")
            
            # Return standardized format or legacy format
            if standardized:
                return self.formatter.format_response(
                    raw_data=result,
                    series_id=series_id,
                    source=DataSource.CACHED,
                    start_time=start_time
                )
            else:
                return result
                
        except Exception as e:
            error_msg = f"Failed to load {series_id}: {str(e)}"
            print(f"❌ {error_msg}")
            
            if standardized:
                return self.formatter.format_response(
                    raw_data=[],
                    series_id=series_id,
                    source=DataSource.CACHED,
                    start_time=start_time,
                    error=error_msg
                )
            else:
                return []
    
    def load_multiple(self, tickers: List[str], date: Optional[str] = None) -> Dict[str, List[Dict]]:
        """
        Load data for multiple tickers concurrently
        
        Args:
            tickers: List of tickers to fetch
            date: Date range for all tickers
            
        Returns:
            Dictionary mapping ticker to data points
        """
        start_time = time.time()
        results = {}
        
        # Parse date once
        start_year, end_year = self._parse_date_range(date)
        
        # Load data for each ticker
        for ticker in tickers:
            try:
                data = self.load_data(ticker, date)
                results[ticker] = data
            except Exception as e:
                print(f"Error loading {ticker}: {e}")
                results[ticker] = []
        
        elapsed = time.time() - start_time
        total_points = sum(len(data) for data in results.values())
        print(f"✅ Loaded {total_points} total data points for {len(tickers)} series in {elapsed:.2f} seconds")
        
        return results
    
    def get_latest(self, ticker: str, n: int = 1) -> List[Dict]:
        """Get the most recent N data points for a ticker"""
        current_year = datetime.now().year
        data = self.load_data(ticker, date=f"{current_year - 1}-{current_year}")
        return data[:n]
    
    def get_available_series(self) -> List[str]:
        """Get list of available data series"""
        available = []
        for series_id in self.series_map.values():
            if self._get_latest_cache_file(series_id):
                available.append(series_id)
        
        # Also check for any other cached files
        pattern = os.path.join(self.cache_dir, "*_latest.json")
        for file in glob.glob(pattern):
            series_id = os.path.basename(file).replace('_latest.json', '')
            if series_id not in available:
                available.append(series_id)
        
        return sorted(available)
    
    def get_data_summary(self, ticker: str) -> Dict:
        """Get summary information about a data series"""
        series_id = self._normalize_series_id(ticker)
        data = self._load_series_from_cache(series_id)
        
        if not data:
            return {"error": "No data available"}
        
        latest = data[-1]  # Assume data is chronologically ordered
        oldest = data[0]
        
        return {
            "series_id": series_id,
            "total_points": len(data),
            "date_range": f"{oldest.date} to {latest.date}",
            "latest_value": latest.value,
            "latest_date": latest.date,
            "years_available": sorted(list(set(dp.year for dp in data)))
        }

# Backward compatibility function
def load_data(ticker: str, date: Optional[str] = None, standardized: bool = False) -> Union[List[Dict], Dict]:
    """
    Simple function to load BLS data (cached version)
    
    Args:
        ticker: Economic indicator ticker
        date: Date range specification
        standardized: Whether to return professional standardized format
        
    Returns:
        Economic data in specified format
    """
    api = FastBLSAPI()
    return api.load_data(ticker, date, standardized=standardized)

# Example usage
if __name__ == "__main__":
    # Initialize API
    bls_api = FastBLSAPI()
    
    # Show available data
    print("=== Available Data Series ===")
    available = bls_api.get_available_series()
    for series in available[:10]:  # Show first 10
        print(f"  {series}")
    
    # Example 1: Load CPI data for last 2 years
    print("\n=== Example 1: CPI Data ===")
    cpi_data = bls_api.load_data('cpi', '2022-2024')
    if cpi_data:
        print(f"Latest CPI: {cpi_data[0]['value']} ({cpi_data[0]['date']})")
        print(f"Data from {cpi_data[-1]['date']} to {cpi_data[0]['date']}")
    
    # Example 2: Load PPI data
    print("\n=== Example 2: PPI Data ===")
    ppi_data = bls_api.load_data('ppi', '2020-2024')
    if ppi_data:
        print(f"Found {len(ppi_data)} PPI data points")
        # Show recent trend
        for point in ppi_data[:5]:
            print(f"  {point['date']}: {point['value']}")
    
    # Example 3: Get data summary
    print("\n=== Example 3: Data Summary ===")
    summary = bls_api.get_data_summary('cpi')
    print(f"CPI Summary: {summary}")
    
    # Example 4: Multiple series
    print("\n=== Example 4: Multiple Series ===")
    multiple_data = bls_api.load_multiple(['cpi', 'ppi'], '2023-2024')
    for ticker, data in multiple_data.items():
        if data:
            print(f"{ticker}: {len(data)} points, latest = {data[0]['value']} ({data[0]['date']})") 