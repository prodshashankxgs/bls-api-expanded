#!/usr/bin/env python3
"""
BLS Data Functions
==================

Easy-to-use functions to get BLS economic data.
Straightforward functions that do what you expect.

Usage:
    from data import get_cpi, get_inflation_data, get_latest_file
    
    # Get CPI data
    cpi_data = get_cpi()
    
    # Get specific categories
    food_data = get_inflation_data("Food")
    energy_data = get_inflation_data("Energy")
"""

import logging
from pathlib import Path
from datetime import datetime
import pandas as pd
from config import Config

# Logging
logger = logging.getLogger(__name__)


def get_latest_file():
    """
    Find the most recent Excel file we downloaded.
    
    Returns:
        Path to the latest Excel file, or None if no files found
    """
    try:
        files = list(Config.DATA_SHEET_DIR.glob(Config.EXCEL_FILE_PATTERN))
        
        if not files:
            logger.warning("no excel files found")
            return None
        
        # Find the most recent file
        latest_file = max(files, key=lambda f: f.stat().st_mtime)
        logger.info(f"using latest file: {latest_file.name}")
        return latest_file
        
    except Exception as e:
        logger.error(f"error finding latest file: {e}")
        return None


def read_excel_data(file_path):
    """
    Read data from an Excel file and return as a simple DataFrame.
    
    Args:
        file_path: Path to the Excel file
        
    Returns:
        pandas DataFrame with the Excel data
    """
    try:
        logger.info(f"reading excel file: {file_path.name}")
        
        # Read the Excel file
        df = pd.read_excel(file_path, engine='openpyxl')
        
        # Clean up column names (remove spaces, make lowercase)
        df.columns = [col.strip().lower().replace(' ', '_') for col in df.columns]
        
        logger.info(f"read {len(df)} rows and {len(df.columns)} columns")
        return df
        
    except Exception as e:
        logger.error(f"error reading excel file: {e}")
        return pd.DataFrame()


def find_category_data(df, category_name):
    """
    Find data for a specific category (like "All items", "Food", etc.)
    
    Args:
        df: DataFrame with BLS data
        category_name: Name of category to find
        
    Returns:
        DataFrame with matching rows
    """
    try:
        # Look for the category in various possible columns
        category_lower = category_name.lower()
        
        # Common column names that might contain categories
        possible_columns = [
            'expenditure_category', 'category', 'item', 'description', 
            'expenditure', 'items', 'product'
        ]
        
        # Find the right column
        category_column = None
        for col in df.columns:
            if any(possible in col.lower() for possible in possible_columns):
                category_column = col
                break
        
        if category_column is None:
            logger.warning("could not find category column")
            return pd.DataFrame()
        
        # Search for the category
        matches = df[df[category_column].str.contains(category_name, case=False, na=False)]
        
        if matches.empty:
            # Try exact match
            matches = df[df[category_column].str.lower() == category_lower]
        
        logger.info(f"found {len(matches)} rows for category '{category_name}'")
        return matches
        
    except Exception as e:
        logger.error(f"error finding category data: {e}")
        return pd.DataFrame()


def get_cpi():
    """
    Get CPI (Consumer Price Index) data.
    
    Returns:
        pandas DataFrame with CPI data
    """
    logger.info("getting cpi data")
    
    # Get the latest file
    latest_file = get_latest_file()
    if latest_file is None:
        return pd.DataFrame()
    
    # Read the data
    df = read_excel_data(latest_file)
    if df.empty:
        return pd.DataFrame()
    
    # Find CPI data
    cpi_data = find_category_data(df, "All items")
    
    if cpi_data.empty:
        logger.warning("no cpi data found")
        return pd.DataFrame()
    
    logger.info(f"retrieved {len(cpi_data)} cpi data points")
    return cpi_data


def get_inflation_data(category="All items"):
    """
    Get inflation data for a specific category.
    
    Args:
        category: Category name (e.g., "Food", "Energy", "All items")
        
    Returns:
        pandas DataFrame with inflation data for that category
    """
    logger.info(f"getting inflation data for: {category}")
    
    # Get the latest file
    latest_file = get_latest_file()
    if latest_file is None:
        return pd.DataFrame()
    
    # Read the data
    df = read_excel_data(latest_file)
    if df.empty:
        return pd.DataFrame()
    
    # Find the specific category
    category_data = find_category_data(df, category)
    
    if category_data.empty:
        logger.warning(f"no data found for category: {category}")
        
        # show available categories to help user
        show_available_categories(df)
        return pd.DataFrame()
    
    logger.info(f"retrieved {len(category_data)} data points for {category}")
    return category_data


def show_available_categories(df):
    """
    Show available categories to help the user.
    
    Args:
        df: DataFrame with BLS data
    """
    try:
        # Find the category column
        category_column = None
        for col in df.columns:
            if 'category' in col.lower() or 'expenditure' in col.lower():
                category_column = col
                break
        
        if category_column is not None:
            categories = df[category_column].dropna().unique()[:10]  # Show first 10
            logger.info("available categories include:")
            for cat in categories:
                logger.info(f"- {cat}")
        
    except Exception as e:
        logger.debug(f"could not show categories: {e}")


def get_food_data():
    """Get food price data"""
    return get_inflation_data("Food")


def get_energy_data():
    """Get energy price data"""
    return get_inflation_data("Energy")


def get_housing_data():
    """Get housing/shelter price data"""
    return get_inflation_data("Shelter")


def get_all_data():
    """
    Get all available data from the latest file.
    
    Returns:
        pandas DataFrame with all data
    """
    logger.info("getting all available data")
    
    latest_file = get_latest_file()
    if latest_file is None:
        return pd.DataFrame()
    
    df = read_excel_data(latest_file)
    
    if not df.empty:
        logger.info(f"retrieved {len(df)} rows of data")
    
    return df


def quick_summary():
    """
    Get a quick summary of the latest inflation data.
    
    Returns:
        Dictionary with key inflation numbers
    """
    logger.info("generating quick inflation summary")
    
    try:
        summary = {}
        
        # Get key categories
        categories = {
            'headline_cpi': 'All items',
            'food': 'Food',
            'energy': 'Energy',
            'shelter': 'Shelter'
        }
        
        for key, category in categories.items():
            data = get_inflation_data(category)
            
            if not data.empty:
                # Try to find recent percentage change data
                pct_columns = [col for col in data.columns if 'pct' in col.lower() and 'change' in col.lower()]
                
                if pct_columns:
                    # Get the most recent percentage change
                    latest_pct = data[pct_columns[0]].iloc[0]
                    try:
                        summary[key] = float(latest_pct)
                    except:
                        summary[key] = latest_pct
                else:
                    summary[key] = "Data available"
            else:
                summary[key] = "No data"
        
        logger.info("summary generated successfully")
        return summary
        
    except Exception as e:
        logger.error(f"error generating summary: {e}")
        return {}


def print_summary():
    """Print a nice summary of current inflation data"""
    summary = quick_summary()
    
    print("\n" + "="*40)
    print("inflation summary")
    print("="*40)
    
    for category, value in summary.items():
        category_name = category.replace('_', ' ').title()
        print(f"{category_name:15}: {value}")
    
    print("="*40)


def test_functions():
    """Test all the functions to make sure they work"""
    print("testing data functions...")
    print("-" * 40)
    
    # test file finding
    latest = get_latest_file()
    if latest:
        print(f"found latest file: {latest.name}")
    else:
        print("no files found")
        return
    
    # test data reading
    all_data = get_all_data()
    if not all_data.empty:
        print(f"read {len(all_data)} rows of data")
        print(f"columns: {list(all_data.columns)[:5]}...")  # show first 5 columns
    else:
        print("could not read data")
        return
    
    # test cpi data
    cpi_data = get_cpi()
    if not cpi_data.empty:
        print(f"got {len(cpi_data)} cpi data points")
    else:
        print("no cpi data found")
    
    # test category data
    food_data = get_food_data()
    if not food_data.empty:
        print(f"got {len(food_data)} food price data points")
    else:
        print("no food data found")
    
    # test summary
    summary = quick_summary()
    if summary:
        print("generated summary successfully")
        print_summary()
    else:
        print("could not generate summary")
    
    print("-" * 40)
    print("testing complete")


if __name__ == "__main__":
    # Run tests when script is called directly
    test_functions()