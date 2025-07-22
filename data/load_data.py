import polars as pl
from typing import List, Optional
import sys
import os

# Add the project root to the path to import bls_scraper
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from bls_scraper import load_data as bls_load_data


class DataLoader:
    """
    A convenient wrapper around the BLS scraper that returns Polars DataFrames
    for multiple tickers at once.
    """
    
    def __init__(self):
        self.ticker_mappings = {
            # Bloomberg-style ticker mappings to BLS series
            "CPSCJEWE Index": "cpi",
            "CPIQWAN Index": "cpi_core", 
            "CPSCWG Index": "cpi_food",
            "CPSCMB Index": "cpi_energy",
            "CPSCINTD Index": "cpi_housing",
            "CPIQSMFN Index": "ppi"
        }
    
    def load_data(self, tickers: List[str], start_date: str) -> pl.DataFrame:
        """
        Load data for multiple tickers and return as a consolidated DataFrame.
        
        Args:
            tickers: List of ticker symbols (Bloomberg-style or BLS style)
            start_date: Start date in format "YYYY-MM-DD" or just "YYYY"
            
        Returns:
            Polars DataFrame with columns: ticker, date, value, series_id, category
        """
        all_data = []
        
        for ticker in tickers:
            # Map Bloomberg-style ticker to BLS series if needed
            bls_ticker = self.ticker_mappings.get(ticker, ticker.lower())
            
            # Extract year from date string for the BLS scraper
            if "-" in start_date:
                start_year = start_date.split("-")[0]
            else:
                start_year = start_date
                
            # Use current year as end year to get latest data
            date_range = f"{start_year}-2025"
            
            # Load data using the BLS scraper
            ticker_data = bls_load_data(bls_ticker, date_range)
            
            # Convert to our format
            for point in ticker_data:
                all_data.append({
                    'ticker': ticker,
                    'date': point['date'],
                    'value': point['value'],
                    'series_id': point['series_id'],
                    'category': point['category'],
                    'year': point['year'],
                    'month': point['month'],
                    'source': point['source']
                })
        
        # Convert to Polars DataFrame
        if all_data:
            df = pl.DataFrame(all_data)
            
            # Convert date column to datetime and sort
            df = df.with_columns([
                pl.col('date').str.to_datetime()
            ]).sort(['ticker', 'date'])
            
            return df
        else:
            # Return empty DataFrame with correct schema
            return pl.DataFrame({
                'ticker': [],
                'date': [],
                'value': [],
                'series_id': [],
                'category': [],
                'year': [],
                'month': [],
                'source': []
            })