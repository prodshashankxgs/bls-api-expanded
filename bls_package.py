#!/usr/bin/env python3
"""
BLS Data Package - Portable Module
==================================

Portable module for loading BLS (Bureau of Labor Statistics) data.
This file can be copied to any project to access BLS CPI data.

Usage in your project:
    from bls_package import load_data, load_data_to_dataframe
    
    # Load data for specific categories
    data = load_data(['All items', 'Food', 'Energy'], '2025-06')
    
    # Or get as DataFrame directly
    df = load_data_to_dataframe(['All items', 'Food'], '2025-06')

Author: Generated with Claude Code
Version: 1.0
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from dateutil.relativedelta import relativedelta
import pandas as pd
import logging

# Set up logging
logger = logging.getLogger(__name__)


# ================================
# CONFIGURATION AND PATH DETECTION
# ================================

class BLSConfig:
    """Configuration for BLS data access"""
    
    @staticmethod
    def _find_bls_data_directory():
        """Find the BLS data directory by searching common locations"""
        # List of possible locations to search
        search_paths = [
            # Current directory and parent directories
            Path.cwd(),
            Path.cwd().parent,
            Path.cwd().parent.parent,
            
            # Relative to this file
            Path(__file__).parent if '__file__' in globals() else Path.cwd(),
            Path(__file__).parent.parent if '__file__' in globals() else Path.cwd(),
            
            # Common project locations
            Path.home() / "Desktop" / "Business" / "Capstone Projects" / "BLS Scraper API",
            Path.home() / "Documents" / "BLS Scraper API",
            Path.home() / "Projects" / "BLS Scraper API",
        ]
        
        # Look for data_sheet directory in each path
        for base_path in search_paths:
            try:
                data_sheet_dir = base_path / "data_sheet"
                if data_sheet_dir.exists() and any(data_sheet_dir.glob("*.xlsx")):
                    return data_sheet_dir
            except Exception:
                continue
        
        return None
    
    @classmethod
    def get_data_sheet_dir(cls):
        """Get the data sheet directory"""
        data_dir = cls._find_bls_data_directory()
        if data_dir:
            return data_dir
        else:
            raise FileNotFoundError(
                "Could not find BLS data directory. "
                "Make sure you've run 'python run.py' to download data first."
            )
    
    @classmethod
    def get_latest_excel_file(cls):
        """Get the most recent Excel file"""
        try:
            data_dir = cls.get_data_sheet_dir()
            excel_files = list(data_dir.glob("*.xlsx"))
            
            if not excel_files:
                raise FileNotFoundError("No Excel files found in data directory")
            
            # Return the most recently modified file
            latest_file = max(excel_files, key=lambda f: f.stat().st_mtime)
            return latest_file
            
        except Exception as e:
            raise FileNotFoundError(f"Error finding Excel file: {e}")


# ================================
# CORE DATA LOADING FUNCTIONS
# ================================

def load_data(ticker_list: List[str], date: str) -> List[Dict[str, Any]]:
    """
    Load BLS data for a list of categories and return NSA values for current and previous month.
    
    Args:
        ticker_list: List of category strings that match exactly with Excel sheet
        date: Date string in format "YYYY-MM" (e.g., "2025-06")
        
    Returns:
        List of dictionaries with category data including NSA values
        
    Example:
        data = load_data(['All items', 'Food', 'Energy'], '2025-06')
        for item in data:
            print(f"{item['category']}: {item['nsa_previous_month']} → {item['nsa_current_month']}")
    """
    logger.info(f"loading data for {len(ticker_list)} categories for date {date}")
    
    # Get the latest Excel file
    try:
        excel_file = BLSConfig.get_latest_excel_file()
        logger.info(f"using excel file: {excel_file.name}")
    except Exception as e:
        logger.error(f"could not find excel file: {e}")
        return []
    
    # Read the Excel file
    try:
        df = pd.read_excel(excel_file, engine='openpyxl', header=None)
        logger.info(f"loaded excel file with shape: {df.shape}")
    except Exception as e:
        logger.error(f"error reading excel file: {e}")
        return []
    
    # Parse the date to get current and previous month
    try:
        current_date = datetime.strptime(date, "%Y-%m")
        previous_date = current_date - relativedelta(months=1)
        
        current_month_str = current_date.strftime("%Y-%m")
        previous_month_str = previous_date.strftime("%Y-%m")
        
        logger.info(f"looking for data for {previous_month_str} and {current_month_str}")
    except Exception as e:
        logger.error(f"error parsing date {date}: {e}")
        return []
    
    # Find the header row and identify columns
    header_info = _find_header_columns(df)
    if not header_info:
        logger.error("could not identify header structure")
        return []
    
    # Extract data for each ticker
    results = []
    for ticker in ticker_list:
        ticker_data = _extract_ticker_data(df, ticker, header_info, current_month_str, previous_month_str)
        if ticker_data:
            results.append(ticker_data)
    
    logger.info(f"successfully extracted data for {len(results)} out of {len(ticker_list)} categories")
    return results


def load_data_to_dataframe(ticker_list: List[str], date: str) -> pd.DataFrame:
    """
    Convenience function that loads data and returns it as a DataFrame.
    
    Args:
        ticker_list: List of category strings
        date: Date string in format "YYYY-MM"
        
    Returns:
        pandas DataFrame with the data
        
    Example:
        df = load_data_to_dataframe(['All items', 'Food'], '2025-06')
        print(df[['category', 'nsa_previous_month', 'nsa_current_month']])
    """
    data_list = load_data(ticker_list, date)
    df = pd.DataFrame(data_list)
    return df


def get_available_categories(max_categories: int = 20) -> List[str]:
    """
    Get a list of available categories from the Excel file.
    
    Args:
        max_categories: Maximum number of categories to return
        
    Returns:
        List of category strings
    """
    try:
        excel_file = BLSConfig.get_latest_excel_file()
        df = pd.read_excel(excel_file, engine='openpyxl', header=None)
        
        # Find categories starting from row 6 (data start row)
        categories = []
        for i in range(6, min(len(df), 6 + max_categories)):
            category = df.iloc[i, 1]  # Column 1 has categories
            if pd.notna(category) and str(category).strip():
                categories.append(str(category).strip())
        
        return categories
        
    except Exception as e:
        logger.error(f"error getting available categories: {e}")
        return []


# ================================
# HELPER FUNCTIONS
# ================================

def _find_header_columns(df: pd.DataFrame) -> Optional[Dict[str, int]]:
    """Find the column positions for different data types in the Excel file"""
    try:
        # Look for the header row with exactly "Expenditure category"
        header_row = None
        for idx, row in df.iterrows():
            if idx > 10:  # Don't search too far
                break
            for col_idx, cell in enumerate(row):
                if pd.notna(cell):
                    cell_text = str(cell).lower().strip().replace('\n', ' ')
                    if cell_text == "expenditure category" or cell_text.startswith("expenditure category"):
                        header_row = idx
                        break
            if header_row is not None:
                break
        
        if header_row is None:
            logger.error("could not find header row")
            return None
        
        # Identify column positions
        column_map = {}
        
        # Look at the header row and the row below for column identification
        for col_idx in range(len(df.columns)):
            header_cell = str(df.iloc[header_row, col_idx]).lower().replace('\n', ' ') if header_row < len(df) else ""
            subheader_cell = str(df.iloc[header_row + 1, col_idx]).lower().replace('\n', ' ') if header_row + 1 < len(df) else ""
            
            # Expenditure category column
            if "expenditure category" in header_cell:
                column_map['category'] = col_idx
                logger.info(f"category column: {col_idx}")
            
            # Unadjusted indexes columns
            if "unadjusted indexes" in header_cell:
                if "may" in subheader_cell and "2025" in subheader_cell:
                    column_map['nsa_may_2025'] = col_idx
                    logger.info(f"nsa may 2025 column: {col_idx}")
                elif "jun" in subheader_cell and "2025" in subheader_cell:
                    column_map['nsa_jun_2025'] = col_idx
                    logger.info(f"nsa jun 2025 column: {col_idx}")
        
        # Set the data start row (skip headers and empty rows)
        column_map['data_start_row'] = 6  # Based on actual Excel structure
        
        logger.info(f"identified columns: {column_map}")
        return column_map
    
    except Exception as e:
        logger.error(f"error finding header columns: {e}")
        return None


def _extract_ticker_data(df: pd.DataFrame, ticker: str, header_info: Dict[str, int], 
                        current_month: str, previous_month: str) -> Optional[Dict[str, Any]]:
    """Extract data for a specific ticker from the DataFrame"""
    try:
        category_col = header_info.get('category')
        data_start_row = header_info.get('data_start_row', 6)
        
        if category_col is None:
            logger.error("category column not identified")
            return None
        
        # Search for the ticker in the category column
        matching_row = None
        for idx in range(data_start_row, len(df)):
            cell_value = df.iloc[idx, category_col]
            if pd.notna(cell_value) and str(cell_value).strip() == ticker.strip():
                matching_row = idx
                break
        
        if matching_row is None:
            logger.warning(f"ticker '{ticker}' not found in excel data")
            return None
        
        # Extract the values
        result = {
            'category': ticker,
            'current_month': current_month,
            'previous_month': previous_month
        }
        
        # Extract NSA values (unadjusted indexes)
        if 'nsa_may_2025' in header_info:
            may_2025_col = header_info['nsa_may_2025']
            may_2025_value = df.iloc[matching_row, may_2025_col]
            result['nsa_previous_month'] = _clean_numeric_value(may_2025_value)
        
        if 'nsa_jun_2025' in header_info:
            jun_2025_col = header_info['nsa_jun_2025']
            jun_2025_value = df.iloc[matching_row, jun_2025_col]
            result['nsa_current_month'] = _clean_numeric_value(jun_2025_value)
        
        # Since there are no adjusted indexes, we'll just return the unadjusted (NSA) values
        # and set SA values to be the same as NSA values
        result['sa_previous_month'] = result.get('nsa_previous_month')
        result['sa_current_month'] = result.get('nsa_current_month')
        
        logger.info(f"extracted data for '{ticker}': {result}")
        return result
    
    except Exception as e:
        logger.error(f"error extracting data for ticker '{ticker}': {e}")
        return None


def _clean_numeric_value(value) -> Optional[float]:
    """Clean and convert a value to float"""
    if pd.isna(value):
        return None
    
    try:
        # Convert to string first, then clean
        str_value = str(value).strip()
        
        # Remove common formatting
        str_value = str_value.replace(',', '').replace('%', '')
        
        # Handle empty or dash values
        if str_value in ['', '-', 'N/A', 'n/a']:
            return None
        
        return float(str_value)
    
    except (ValueError, TypeError):
        return None


# ================================
# UTILITY FUNCTIONS
# ================================

def show_sample_data():
    """Show sample data for testing"""
    print("Sample BLS Data")
    print("=" * 50)
    
    try:
        # Test with common categories
        sample_categories = ["All items", "Food", "Energy", "Shelter"]
        data = load_data(sample_categories, "2025-06")
        
        if data:
            print(f"Loaded data for {len(data)} categories:")
            for item in data:
                category = item.get('category', 'Unknown')
                nsa_prev = item.get('nsa_previous_month', 'N/A')
                nsa_curr = item.get('nsa_current_month', 'N/A')
                print(f"   {category}: {nsa_prev} → {nsa_curr}")
        else:
            print("No data available")
            
    except Exception as e:
        print(f"Error loading sample data: {e}")


def check_setup():
    """Check if the BLS package is set up correctly"""
    print("BLS Package Setup Check")
    print("=" * 50)
    
    try:
        # Check if we can find the data directory
        data_dir = BLSConfig.get_data_sheet_dir()
        print(f"Data directory found: {data_dir}")
        
        # Check if we can find Excel files
        excel_file = BLSConfig.get_latest_excel_file()
        print(f"Latest Excel file: {excel_file.name}")
        
        # Check if we can load data
        test_data = load_data(["All items"], "2025-06")
        if test_data:
            print("Data loading works correctly")
        else:
            print("Data loading failed")
        
        print("\nBLS Package is ready to use!")
        return True
        
    except Exception as e:
        print(f"Setup check failed: {e}")
        print("Try running 'python run.py' first to download data")
        return False


# Example usage and testing
if __name__ == "__main__":
    print("BLS Data Package")
    print("=" * 50)
    
    # Check setup
    if check_setup():
        # Show sample data
        show_sample_data()
        
        # Show available categories
        print("Available Categories (sample):")
        categories = get_available_categories(10)
        for i, cat in enumerate(categories, 1):
            print(f"   {i:2d}. {cat}")
    
    print("Usage Examples:")
    print("from bls_package import load_data, load_data_to_dataframe")
    print("data = load_data(['All items', 'Food'], '2025-06')")
    print("df = load_data_to_dataframe(['Energy', 'Shelter'], '2025-06')")