#!/usr/bin/env python3
"""
Ultra-Fresh BLS Data Scraper

This scraper is specifically designed to get the absolute most recent economic data
available, checking multiple sources and ensuring maximum freshness for trading systems.
"""

import requests
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union
import re
from dataclasses import dataclass
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
import calendar

# Import the standardized schema
from .standardized_schema import (
    standardize_data, DataSource, StandardizedDataFormatter
)

@dataclass
class FreshDataPoint:
    """Enhanced data structure with freshness tracking"""
    series_id: str
    date: str
    value: float
    period: str
    year: int
    month: Optional[int] = None
    scraped_timestamp: str = ""
    source_url: str = ""
    data_vintage: str = ""  # When this data was originally released

class UltraFreshScraper:
    """Ultra-fresh economic data scraper - maximum recency guaranteed"""
    
    def __init__(self, max_workers: int = 10):
        self.max_workers = max_workers
        self.formatter = StandardizedDataFormatter()
        
        # Multiple data sources for maximum freshness
        self.data_sources = {
            'cpi': [
                'https://fred.stlouisfed.org/graph/fredgraph.csv?id=CPIAUCSL',
                'https://beta.bls.gov/dataViewer/view/timeseries/CPIAUCSL',
                'https://api.stlouisfed.org/fred/series/observations?series_id=CPIAUCSL&api_key=demo&file_type=json',
            ],
            'cpi_core': [
                'https://fred.stlouisfed.org/graph/fredgraph.csv?id=CPILFESL',
                'https://beta.bls.gov/dataViewer/view/timeseries/CPILFESL',
            ],
            'ppi': [
                'https://fred.stlouisfed.org/graph/fredgraph.csv?id=PPIFIS',
                'https://beta.bls.gov/dataViewer/view/timeseries/PPIFIS',
            ],
            'unemployment': [
                'https://fred.stlouisfed.org/graph/fredgraph.csv?id=UNRATE',
                'https://beta.bls.gov/dataViewer/view/timeseries/UNRATE',
            ]
        }
        
        # Series metadata
        self.series_map = {
            'cpi': 'CPIAUCSL',
            'cpi_core': 'CPILFESL', 
            'ppi': 'PPIFIS',
            'unemployment': 'UNRATE'
        }
        
        # Create session with aggressive headers for freshness
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'no-cache',  # Force fresh data
            'Pragma': 'no-cache'
        })

    def get_freshest_data(self, ticker: str, months_back: int = 6) -> List[FreshDataPoint]:
        """
        Get the freshest possible data using multiple concurrent sources
        
        Args:
            ticker: Economic indicator ('cpi', 'ppi', etc.)
            months_back: How many months back to retrieve
            
        Returns:
            List of ultra-fresh data points
        """
        ticker_lower = ticker.lower().strip()
        series_id = self.series_map.get(ticker_lower, ticker.upper())
        
        print(f"🚀 ULTRA-FRESH SCRAPING: {ticker.upper()} (checking {len(self.data_sources.get(ticker_lower, []))} sources)")
        
        all_results = []
        sources = self.data_sources.get(ticker_lower, [])
        
        # Scrape all sources concurrently for maximum speed
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {}
            
            for i, source_url in enumerate(sources):
                if 'fred' in source_url and 'csv' in source_url:
                    future = executor.submit(self._scrape_fred_csv_fresh, source_url, series_id, months_back)
                elif 'beta.bls' in source_url:
                    future = executor.submit(self._scrape_bls_beta_fresh, source_url, series_id, months_back)
                elif 'api.stlouisfed' in source_url:
                    future = executor.submit(self._scrape_fred_api_fresh, source_url, series_id, months_back)
                else:
                    continue
                    
                futures[future] = f"source_{i+1}"
            
            # Collect results as they complete
            for future in as_completed(futures):
                source_name = futures[future]
                try:
                    result = future.result(timeout=10)
                    if result:
                        print(f"✅ {source_name}: Found {len(result)} fresh data points")
                        all_results.extend(result)
                    else:
                        print(f"⚠️ {source_name}: No data returned")
                except Exception as e:
                    print(f"❌ {source_name}: Error - {str(e)[:50]}...")
        
        # Deduplicate and find the absolute freshest data
        return self._get_freshest_points(all_results)
    
    def _scrape_fred_csv_fresh(self, url: str, series_id: str, months_back: int) -> List[FreshDataPoint]:
        """Scrape FRED CSV with cache-busting for maximum freshness"""
        try:
            # Add cache-busting parameters
            fresh_url = f"{url}&vintage_dates={datetime.now().strftime('%Y-%m-%d')}&_={int(time.time())}"
            
            response = self.session.get(fresh_url, timeout=10)
            response.raise_for_status()
            
            lines = response.text.strip().split('\n')
            if len(lines) < 2:
                return []
            
            # Parse CSV data
            data_points = []
            cutoff_date = datetime.now() - timedelta(days=months_back * 32)
            
            for line in lines[1:]:  # Skip header
                if ',' not in line:
                    continue
                    
                try:
                    date_str, value_str = line.split(',', 1)
                    
                    if value_str.strip() in ['.', '', 'NA']:
                        continue
                        
                    date_obj = datetime.strptime(date_str.strip(), '%Y-%m-%d')
                    if date_obj < cutoff_date:
                        continue
                    
                    value = float(value_str.strip())
                    
                    data_point = FreshDataPoint(
                        series_id=series_id,
                        date=date_str.strip(),
                        value=value,
                        period=f"{date_obj.year}-{date_obj.month:02d}",
                        year=date_obj.year,
                        month=date_obj.month,
                        scraped_timestamp=datetime.now().isoformat(),
                        source_url=url,
                        data_vintage="latest"
                    )
                    data_points.append(data_point)
                    
                except (ValueError, IndexError):
                    continue
            
            return data_points
            
        except Exception as e:
            print(f"FRED CSV error: {e}")
            return []
    
    def _scrape_bls_beta_fresh(self, url: str, series_id: str, months_back: int) -> List[FreshDataPoint]:
        """Scrape BLS beta site with fresh headers"""
        try:
            # Force fresh request
            fresh_headers = self.session.headers.copy()
            fresh_headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            fresh_headers['Pragma'] = 'no-cache'
            fresh_headers['Expires'] = '0'
            
            response = self.session.get(url, headers=fresh_headers, timeout=15)
            if response.status_code != 200:
                return []
                
            # Basic parsing - BLS beta site structure varies
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for data tables or JSON data
            data_points = []
            script_tags = soup.find_all('script')
            
            for script in script_tags:
                if script.string and 'data' in script.string.lower():
                    # Try to extract data from JavaScript
                    content = script.string
                    if series_id in content:
                        # This is a simplified parser - BLS structure is complex
                        # In production, would need more sophisticated parsing
                        print(f"Found potential data in BLS beta for {series_id}")
                        break
            
            return data_points
            
        except Exception as e:
            print(f"BLS beta error: {e}")
            return []
    
    def _scrape_fred_api_fresh(self, url: str, series_id: str, months_back: int) -> List[FreshDataPoint]:
        """Scrape FRED API (demo key) for freshest data"""
        try:
            # FRED API with recent data
            cutoff_date = (datetime.now() - timedelta(days=months_back * 32)).strftime('%Y-%m-%d')
            fresh_url = f"{url}&observation_start={cutoff_date}&sort_order=desc"
            
            response = self.session.get(fresh_url, timeout=10)
            if response.status_code != 200:
                return []
                
            data = response.json()
            if 'observations' not in data:
                return []
            
            data_points = []
            for obs in data['observations']:
                if obs['value'] in ['.', '', 'NA']:
                    continue
                    
                try:
                    date_obj = datetime.strptime(obs['date'], '%Y-%m-%d')
                    value = float(obs['value'])
                    
                    data_point = FreshDataPoint(
                        series_id=series_id,
                        date=obs['date'],
                        value=value,
                        period=f"{date_obj.year}-{date_obj.month:02d}",
                        year=date_obj.year,
                        month=date_obj.month,
                        scraped_timestamp=datetime.now().isoformat(),
                        source_url=url,
                        data_vintage=obs.get('realtime_end', 'latest')
                    )
                    data_points.append(data_point)
                    
                except (ValueError, KeyError):
                    continue
            
            return data_points
            
        except Exception as e:
            print(f"FRED API error: {e}")
            return []
    
    def _get_freshest_points(self, all_points: List[FreshDataPoint]) -> List[FreshDataPoint]:
        """Find the absolutely freshest data points from all sources"""
        if not all_points:
            return []
        
        # Group by date and find the freshest for each date
        date_groups = {}
        for point in all_points:
            date_key = point.date
            if date_key not in date_groups:
                date_groups[date_key] = []
            date_groups[date_key].append(point)
        
        # Select the freshest point for each date
        freshest_points = []
        for date_key, points in date_groups.items():
            # Sort by scrape timestamp (most recent first)
            points.sort(key=lambda x: x.scraped_timestamp, reverse=True)
            freshest_points.append(points[0])
        
        # Sort by date (most recent first)
        freshest_points.sort(key=lambda x: x.date, reverse=True)
        
        print(f"🔥 Selected {len(freshest_points)} ultra-fresh data points")
        return freshest_points
    
    def load_freshest_data(self, ticker: str, months_back: int = 6, standardized: bool = True) -> Union[List[Dict], Dict]:
        """
        Load the absolute freshest economic data available
        
        Args:
            ticker: Economic indicator ticker
            months_back: How many months back to retrieve
            standardized: Whether to return professional standardized format
            
        Returns:
            Ultra-fresh economic data
        """
        start_time = time.time()
        
        try:
            # Get freshest data points
            fresh_points = self.get_freshest_data(ticker, months_back)
            
            if not fresh_points:
                error_msg = f"No fresh data available for {ticker}"
                if standardized:
                    return self.formatter.format_response(
                        raw_data=[],
                        series_id=self.series_map.get(ticker.lower(), ticker.upper()),
                        source=DataSource.LIVE_SCRAPED,
                        start_time=start_time,
                        error=error_msg
                    )
                else:
                    return []
            
            # Convert to standard format
            result = []
            for point in fresh_points:
                result.append({
                    'series_id': point.series_id,
                    'date': point.date,
                    'value': point.value,
                    'period': point.period,
                    'year': point.year,
                    'month': point.month,
                    'scraped_at': point.scraped_timestamp,
                    'source': 'ultra_fresh',
                    'source_url': point.source_url,
                    'data_vintage': point.data_vintage
                })
            
            elapsed = time.time() - start_time
            print(f"⚡ ULTRA-FRESH: {len(result)} points in {elapsed:.2f}s")
            
            # Return in requested format
            if standardized:
                return self.formatter.format_response(
                    raw_data=result,
                    series_id=self.series_map.get(ticker.lower(), ticker.upper()),
                    source=DataSource.LIVE_SCRAPED,
                    start_time=start_time
                )
            else:
                return result
                
        except Exception as e:
            error_msg = f"Ultra-fresh scraping failed for {ticker}: {str(e)}"
            print(f"❌ {error_msg}")
            
            if standardized:
                return self.formatter.format_response(
                    raw_data=[],
                    series_id=self.series_map.get(ticker.lower(), ticker.upper()),
                    source=DataSource.LIVE_SCRAPED,
                    start_time=start_time,
                    error=error_msg
                )
            else:
                return []

# Convenience function for ultra-fresh data
def get_freshest_data(ticker: str, months_back: int = 6, standardized: bool = True) -> Union[List[Dict], Dict]:
    """
    Get the absolute freshest economic data available
    
    Args:
        ticker: Economic indicator ticker (cpi, ppi, unemployment)
        months_back: How many months back to retrieve (default 6)
        standardized: Whether to return professional format (default True)
        
    Returns:
        Ultra-fresh economic data with maximum recency
    """
    scraper = UltraFreshScraper()
    return scraper.load_freshest_data(ticker, months_back, standardized)

# Example usage
if __name__ == "__main__":
    print("⚡ Ultra-Fresh BLS Data Scraper")
    print("="*50)
    
    # Test ultra-fresh scraping
    print("\n🔥 Getting ultra-fresh CPI data...")
    fresh_data = get_freshest_data('cpi', months_back=3, standardized=True)
    
    if isinstance(fresh_data, dict) and fresh_data.get('success'):
        metadata = fresh_data['metadata']
        print(f"✅ Success! {metadata['total_points']} ultra-fresh points in {metadata['latency_ms']}ms")
        
        if fresh_data['data']:
            latest = fresh_data['data'][0]
            print(f"📊 Latest: {latest['date']} = {latest['value']}")
            print(f"🕐 Scraped: {latest.get('scraped_at', 'N/A')}")
            
    else:
        print("❌ Ultra-fresh scraping failed")
        if isinstance(fresh_data, dict):
            print(f"Error: {fresh_data.get('error', 'Unknown')}") 