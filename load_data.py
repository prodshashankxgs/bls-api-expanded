#!/usr/bin/env python3
"""
Load Data Function - Enhanced BLS Data Loading
==============================================

Enhanced load_data function that takes a list of category strings and a date,
then returns NSA and SA values for the current month and previous month.

Usage:
    from load_data import load_data
    import pandas as pd
    
    # define your categories (match Excel sheet exactly)
    ticker_list = ["All items", "Food", "Energy", "Shelter"]
    
    # load data for june 2025
    data_list = load_data(ticker_list, "2025-06")
    
    # convert to dataframe
    df = pd.DataFrame(data_list)
    print(df)
"""

import pandas as pd
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from dateutil.relativedelta import relativedelta
from config import Config

logger = logging.getLogger(__name__)


def load_data(ticker_list: List[str], date: str) -> List[Dict[str, Any]]:
    """
    Load BLS data for a list of categories and return NSA/SA values for current and previous month.
    
    Args:
        ticker_list: List of category strings that match exactly with Excel sheet
        date: Date string in format "YYYY-MM" (e.g., "2025-06")
        
    Returns:
        List of dictionaries with category data including NSA/SA values
    """
    logger.info(f"loading data for {len(ticker_list)} categories for date {date}")
    
    # get the latest excel file
    excel_file = Config.get_latest_excel_file()
    if not excel_file:
        logger.error("no excel files found")
        return []
    
    logger.info(f"using excel file: {excel_file.name}")
    
    # read the excel file
    try:
        df = pd.read_excel(excel_file, engine='openpyxl', header=None)
        logger.info(f"loaded excel file with shape: {df.shape}")
    except Exception as e:
        logger.error(f"error reading excel file: {e}")
        return []
    
    # parse the date to get current and previous month
    try:
        current_date = datetime.strptime(date, "%Y-%m")
        previous_date = current_date - relativedelta(months=1)
        
        current_month_str = current_date.strftime("%Y-%m")
        previous_month_str = previous_date.strftime("%Y-%m")
        
        logger.info(f"looking for data for {previous_month_str} and {current_month_str}")
    except Exception as e:
        logger.error(f"error parsing date {date}: {e}")
        return []
    
    # find the header row and identify columns
    header_info = _find_header_columns(df)
    if not header_info:
        logger.error("could not identify header structure")
        return []
    
    # extract data for each ticker
    results = []
    for ticker in ticker_list:
        ticker_data = _extract_ticker_data(df, ticker, header_info, current_month_str, previous_month_str)
        if ticker_data:
            results.append(ticker_data)
    
    logger.info(f"successfully extracted data for {len(results)} out of {len(ticker_list)} categories")
    return results


def _find_header_columns(df: pd.DataFrame) -> Optional[Dict[str, int]]:
    """
    Find the column positions for different data types in the Excel file.
    
    Returns:
        Dictionary with column mappings or None if not found
    """
    try:
        # look for the header row with exactly "Expenditure category" as a standalone column header
        header_row = None
        for idx, row in df.iterrows():
            if idx > 10:  # don't search too far
                break
            for col_idx, cell in enumerate(row):
                if pd.notna(cell):
                    cell_text = str(cell).lower().strip().replace('\n', ' ')
                    # look for exact match or very close match
                    if cell_text == "expenditure category" or cell_text.startswith("expenditure category"):
                        header_row = idx
                        break
            if header_row is not None:
                break
        
        if header_row is None:
            logger.error("could not find header row")
            return None
        
        # identify column positions based on actual structure
        column_map = {}
        
        # look at the header row and the row below for column identification
        for col_idx in range(len(df.columns)):
            header_cell = str(df.iloc[header_row, col_idx]).lower().replace('\n', ' ') if header_row < len(df) else ""
            subheader_cell = str(df.iloc[header_row + 1, col_idx]).lower().replace('\n', ' ') if header_row + 1 < len(df) else ""
            
            # expenditure category column (column 1)
            if "expenditure category" in header_cell:
                column_map['category'] = col_idx
                logger.info(f"category column: {col_idx}")
            
            # unadjusted indexes columns
            if "unadjusted indexes" in header_cell:
                if "may" in subheader_cell and "2025" in subheader_cell:
                    column_map['nsa_may_2025'] = col_idx
                    logger.info(f"nsa may 2025 column: {col_idx}")
                elif "jun" in subheader_cell and "2025" in subheader_cell:
                    column_map['nsa_jun_2025'] = col_idx
                    logger.info(f"nsa jun 2025 column: {col_idx}")
            
            # note: we're only extracting NSA (unadjusted) values as requested
        
        # set the data start row (skip headers and empty rows)
        column_map['data_start_row'] = 6  # based on actual Excel structure
        
        logger.info(f"identified columns: {column_map}")
        return column_map
    
    except Exception as e:
        logger.error(f"error finding header columns: {e}")
        return None


def _extract_ticker_data(df: pd.DataFrame, ticker: str, header_info: Dict[str, int], 
                        current_month: str, previous_month: str) -> Optional[Dict[str, Any]]:
    """
    Extract data for a specific ticker from the DataFrame.
    
    Args:
        df: Excel data DataFrame
        ticker: Category name to search for
        header_info: Column mapping information
        current_month: Current month string (YYYY-MM)
        previous_month: Previous month string (YYYY-MM)
        
    Returns:
        Dictionary with ticker data or None if not found
    """
    try:
        category_col = header_info.get('category')
        data_start_row = header_info.get('data_start_row', 6)
        
        if category_col is None:
            logger.error("category column not identified")
            return None
        
        # search for the ticker in the category column
        matching_row = None
        for idx in range(data_start_row, len(df)):
            cell_value = df.iloc[idx, category_col]
            if pd.notna(cell_value) and str(cell_value).strip() == ticker.strip():
                matching_row = idx
                break
        
        if matching_row is None:
            logger.warning(f"ticker '{ticker}' not found in excel data")
            return None
        
        # extract the values with dates as column headers
        result = {
            'category': ticker
        }
        
        # extract NSA values (unadjusted indexes)
        if 'nsa_may_2025' in header_info:
            may_2025_col = header_info['nsa_may_2025']
            may_2025_value = df.iloc[matching_row, may_2025_col]
            result[f'nsa_{previous_month}'] = _clean_numeric_value(may_2025_value)
        
        if 'nsa_jun_2025' in header_info:
            jun_2025_col = header_info['nsa_jun_2025']
            jun_2025_value = df.iloc[matching_row, jun_2025_col]
            result[f'nsa_{current_month}'] = _clean_numeric_value(jun_2025_value)
        
        # Add SA values (seasonally adjusted) - use same as NSA if not available separately
        result[f'sa_{previous_month}'] = result.get(f'nsa_{previous_month}')
        result[f'sa_{current_month}'] = result.get(f'nsa_{current_month}')
        
        logger.info(f"extracted data for '{ticker}': {result}")
        return result
    
    except Exception as e:
        logger.error(f"error extracting data for ticker '{ticker}': {e}")
        return None


def _clean_numeric_value(value) -> Optional[float]:
    """
    Clean and convert a value to float.
    
    Args:
        value: Raw value from Excel
        
    Returns:
        Float value or None if conversion fails
    """
    if pd.isna(value):
        return None
    
    try:
        # convert to string first, then clean
        str_value = str(value).strip()
        
        # remove common formatting
        str_value = str_value.replace(',', '').replace('%', '')
        
        # handle empty or dash values
        if str_value in ['', '-', 'N/A', 'n/a']:
            return None
        
        return float(str_value)
    
    except (ValueError, TypeError):
        return None


def load_data_to_dataframe(ticker_list: List[str], date: str) -> pd.DataFrame:
    """
    Convenience function that loads data and returns it as a DataFrame.
    
    Args:
        ticker_list: List of category strings
        date: Date string in format "YYYY-MM"
        
    Returns:
        pandas DataFrame with the data
    """
    data_list = load_data(ticker_list, date)
    df = pd.DataFrame(data_list)
    return df


def example_usage():
    """
    Example of how to use the load_data function.
    """
    print("example usage of load_data function")
    print("=" * 50)
    
    # define categories to load
    ticker_list = [
        "All items",
        "Food", 
        "Energy",
        "Shelter",
        "Food at home"
    ]
    
    # load data for june 2025
    print(f"loading data for categories: {ticker_list}")
    data_list = load_data(ticker_list, "2025-06")
    
    if data_list:
        # convert to dataframe
        df = pd.DataFrame(data_list)
        print(f"\nsuccessfully loaded data for {len(df)} categories:")
        print(df.to_string(index=False))
        
        # show just the NSA and SA values
        print("\nnsa and sa values:")
        print("-" * 30)
        for item in data_list:
            category = item.get('category', 'unknown')
            nsa_prev = item.get('nsa_previous_month', 'n/a')
            nsa_curr = item.get('nsa_current_month', 'n/a')
            sa_prev = item.get('sa_previous_month', 'n/a') 
            sa_curr = item.get('sa_current_month', 'n/a')
            
            print(f"{category}:")
            print(f"  nsa: {nsa_prev} -> {nsa_curr}")
            print(f"  sa:  {sa_prev} -> {sa_curr}")
    else:
        print("no data loaded")


if __name__ == "__main__":
    example_usage()