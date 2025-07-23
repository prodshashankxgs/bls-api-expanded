#!/usr/bin/env python3
"""
BLS Economic Data Loader
========================

A clean, production-ready interface for loading US Bureau of Labor Statistics economic data.

Usage:
    from data_loader import DataLoader
    
    tickers = ["cpi", "unemployment", "ppi"]
    dl = DataLoader()
    df = dl.load_data(tickers, "2022-2025")
    print(df)

Supported Indicators:
    - cpi: Consumer Price Index
    - cpi_core: Core CPI (Less Food and Energy)
    - cpi_food: Food Consumer Price Index
    - cpi_energy: Energy Consumer Price Index
    - cpi_housing: Housing Consumer Price Index  
    - ppi: Producer Price Index
    - unemployment: Unemployment Rate

The data is sourced directly from BLS timeseries tables with historical coverage
from when each series began (some from 1913) through the most recent data.
"""

import polars as pl
import requests
from datetime import datetime
from typing import List, Dict, Optional, Union
import sys
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataLoader:
    """
    Production-ready BLS Economic Data Loader
    
    Provides a clean interface to load economic indicators from the BLS API.
    Automatically handles caching, retries, and data formatting.
    """
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize the DataLoader
        
        Args:
            base_url: URL of the BLS API server (default: http://localhost:8000)
        """
        self.base_url = base_url
        self.session = requests.Session()
        self.session.timeout = 30
        
        # Available indicators with descriptions
        self.indicators = {
            'cpi': 'Consumer Price Index (All Items)',
            'cpi_core': 'Core CPI (Less Food and Energy)',
            'cpi_food': 'Food Consumer Price Index',
            'cpi_energy': 'Energy Consumer Price Index',
            'cpi_housing': 'Housing Consumer Price Index',
            'ppi': 'Producer Price Index',
            'unemployment': 'Unemployment Rate'
        }
    
    def get_available_indicators(self) -> Dict[str, str]:
        """Get dictionary of available indicators and their descriptions"""
        return self.indicators.copy()
    
    def load_single_indicator(self, ticker: str, date_range: Optional[str] = None) -> Optional[Dict]:
        """
        Load data for a single economic indicator
        
        Args:
            ticker: Economic indicator code (e.g., 'cpi', 'unemployment')
            date_range: Optional date range (e.g., '2022-2025', '2023')
            
        Returns:
            Dictionary with API response or None if failed
        """
        ticker = ticker.lower().strip()
        
        # Check if ticker is supported
        if ticker not in self.indicators:
            logger.warning(f"Ticker '{ticker}' not supported. Available: {list(self.indicators.keys())}")
            return None
        
        try:
            url = f"{self.base_url}/data/{ticker}"
            params = {}
            if date_range:
                params['date'] = date_range
            
            response = self.session.get(url, params=params)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to load {ticker}: HTTP {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error loading {ticker}: {e}")
            return None
    
    def load_data(self, tickers: Union[str, List[str]], date_range: Optional[str] = None) -> pl.DataFrame:
        """
        Load economic data for one or more indicators
        
        Args:
            tickers: Single ticker string or list of ticker strings
            date_range: Optional date range (e.g., '2022-2025', 'last 3 years')
            
        Returns:
            Polars DataFrame with economic data
            
        Example:
            # Single indicator
            df = dl.load_data("cpi", "2022-2025")
            
            # Multiple indicators  
            df = dl.load_data(["cpi", "unemployment"], "2023")
            
        DataFrame Columns:
            - ticker: Indicator code
            - category: Full indicator name
            - date: Date (YYYY-MM-DD format)
            - value: Index value or percentage
            - year: Year
            - month: Month (1-12)
            - period: Human-readable period (e.g., "January 2025")
            - source: Data source
        """
        # Handle single ticker input
        if isinstance(tickers, str):
            tickers = [tickers]
        
        all_data = []
        successful_tickers = []
        failed_tickers = []
        
        logger.info(f"Loading data for {len(tickers)} indicator(s): {tickers}")
        
        for ticker in tickers:
            logger.info(f"Loading {ticker}...")
            
            result = self.load_single_indicator(ticker, date_range)
            
            if result and result.get('data'):
                ticker_data = result['data']
                category = self.indicators.get(ticker, f"Unknown: {ticker}")
                successful_tickers.append(ticker)
                
                # Process each data point
                for row in ticker_data:
                    # Create standardized data structure
                    data_point = {
                        'ticker': ticker,
                        'category': category,
                        'value': row.get('value', 0.0),
                        'year': row.get('year', 0),
                        'month': row.get('month', 0),
                        'series_id': row.get('series_id', ''),
                        'source': row.get('source', 'bls')
                    }
                    all_data.append(data_point)
            else:
                failed_tickers.append(ticker)
                logger.warning(f"No data found for {ticker}")
        
        if not all_data:
            logger.error("No data loaded! Ensure the BLS API server is running.")
            return pl.DataFrame()
        
        # Create Polars DataFrame
        df = pl.DataFrame(all_data)
        
        # Add computed columns
        df = df.with_columns([
            # Create date column
            pl.date(pl.col('year'), pl.col('month'), 1).alias('date'),
            
            # Create month names
            pl.when(pl.col('month') == 1).then(pl.lit('January'))
            .when(pl.col('month') == 2).then(pl.lit('February'))
            .when(pl.col('month') == 3).then(pl.lit('March'))
            .when(pl.col('month') == 4).then(pl.lit('April'))
            .when(pl.col('month') == 5).then(pl.lit('May'))
            .when(pl.col('month') == 6).then(pl.lit('June'))
            .when(pl.col('month') == 7).then(pl.lit('July'))
            .when(pl.col('month') == 8).then(pl.lit('August'))
            .when(pl.col('month') == 9).then(pl.lit('September'))
            .when(pl.col('month') == 10).then(pl.lit('October'))
            .when(pl.col('month') == 11).then(pl.lit('November'))
            .when(pl.col('month') == 12).then(pl.lit('December'))
            .alias('month_name')
        ])
        
        # Create period column (e.g., "January 2025")
        df = df.with_columns([
            (pl.col('month_name') + ' ' + pl.col('year').cast(pl.Utf8)).alias('period')
        ])
        
        # Sort by ticker and date (most recent first)
        df = df.sort(['ticker', 'date'], descending=[False, True])
        
        # Select final columns in logical order
        df = df.select([
            'ticker', 'category', 'period', 'date', 'year', 'month', 
            'value', 'series_id', 'source'
        ])
        
        logger.info(f"Successfully loaded {len(df)} data points for {len(successful_tickers)} indicators")
        if failed_tickers:
            logger.warning(f"Failed to load: {failed_tickers}")
        
        return df
    
    def get_wide_format(self, df: pl.DataFrame) -> pl.DataFrame:
        """
        Convert DataFrame to wide format (dates as rows, tickers as columns)
        
        Args:
            df: DataFrame from load_data()
            
        Returns:
            Wide format DataFrame suitable for time series analysis
        """
        if df.is_empty():
            return df
        
        try:
            wide_df = df.pivot(
                values='value',
                index='date',
                on='ticker',
                aggregate_function='mean'
            ).sort('date', descending=True)
            
            return wide_df
        except Exception as e:
            logger.error(f"Error creating wide format: {e}")
            return pl.DataFrame()
    
    def get_summary(self, df: pl.DataFrame) -> pl.DataFrame:
        """
        Get summary statistics for loaded data
        
        Args:
            df: DataFrame from load_data()
            
        Returns:
            Summary DataFrame with statistics by ticker
        """
        if df.is_empty():
            return df
        
        summary = df.group_by('ticker').agg([
            pl.col('category').first().alias('indicator_name'),
            pl.col('value').count().alias('data_points'),
            pl.col('value').min().alias('min_value'),
            pl.col('value').max().alias('max_value'),
            pl.col('value').mean().round(3).alias('avg_value'),
            pl.col('date').min().alias('start_date'),
            pl.col('date').max().alias('end_date'),
            pl.col('source').first().alias('data_source')
        ]).sort('ticker')
        
        return summary
    
    def save_data(self, df: pl.DataFrame, filename: str, format: str = 'csv') -> bool:
        """
        Save DataFrame to file
        
        Args:
            df: DataFrame to save
            filename: Output filename
            format: File format ('csv' or 'parquet')
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if format.lower() == 'csv':
                df.write_csv(filename)
            elif format.lower() == 'parquet':
                df.write_parquet(filename)
            else:
                logger.error(f"Unsupported format: {format}")
                return False
            
            logger.info(f"Saved {len(df)} rows to {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving file: {e}")
            return False
    
    def health_check(self) -> bool:
        """
        Check if the BLS API server is running and responsive
        
        Returns:
            True if server is healthy, False otherwise
        """
        try:
            response = self.session.get(f"{self.base_url}/health")
            return response.status_code == 200
        except:
            return False


# Convenience functions for direct usage
def load_cpi_data(date_range: Optional[str] = None) -> pl.DataFrame:
    """Quick function to load CPI data"""
    dl = DataLoader()
    return dl.load_data("cpi", date_range)

def load_unemployment_data(date_range: Optional[str] = None) -> pl.DataFrame:
    """Quick function to load unemployment data"""
    dl = DataLoader()
    return dl.load_data("unemployment", date_range)

def load_multiple_indicators(tickers: List[str], date_range: Optional[str] = None) -> pl.DataFrame:
    """Quick function to load multiple indicators"""
    dl = DataLoader()
    return dl.load_data(tickers, date_range)


if __name__ == "__main__":
    # Example usage when run directly
    print("BLS Economic Data Loader")
    print("=" * 50)
    
    # Initialize loader
    dl = DataLoader()
    
    # Check server health
    if not dl.health_check():
        print("❌ BLS API server is not running!")
        print("Please start the server first: python3 run.py")
        sys.exit(1)
    
    print("✅ BLS API server is running")
    print("\nAvailable indicators:")
    for ticker, name in dl.get_available_indicators().items():
        print(f"  {ticker}: {name}")
    
    # Load sample data
    print("\nLoading sample CPI data...")
    df = dl.load_data("cpi", "2023-2025")
    
    if not df.is_empty():
        print(f"Loaded {len(df)} data points")
        print("\nSample data:")
        print(df.head(10))
        
        print("\nSummary:")
        print(dl.get_summary(df))
    else:
        print("No data loaded")