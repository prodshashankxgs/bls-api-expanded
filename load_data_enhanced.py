#!/usr/bin/env python3
"""
Enhanced Load Data Function - BLS Data Loading with NSA/SA Support
================================================================

Enhanced load_data function that fetches both NSA (Not Seasonally Adjusted) and 
SA (Seasonally Adjusted) data with dates as column headers.

New Data Structure:
    {
        "category": "All items",
        "nsa_2025-05": 309.1,
        "nsa_2025-06": 310.3,
        "sa_2025-05": 308.5,
        "sa_2025-06": 309.8
    }

Usage:
    from load_data_enhanced import load_data
    import pandas as pd
    
    # Define categories
    ticker_list = ["All items", "Food", "Energy", "Shelter"]
    
    # Load data for June 2025
    data_list = load_data(ticker_list, "2025-06")
    
    # Convert to DataFrame
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
    Load BLS data with both NSA and SA values, using dates as column headers.
    
    Args:
        ticker_list: List of category strings that match exactly with Excel sheet
        date: Date string in format "YYYY-MM" (e.g., "2025-06")
        
    Returns:
        List of dictionaries with structure:
        {
            "category": "All items",
            "nsa_2025-05": 309.1,
            "nsa_2025-06": 310.3,
            "sa_2025-05": 308.5,
            "sa_2025-06": 309.8
        }
    """
    logger.info(f"loading NSA/SA data for {len(ticker_list)} categories for date {date}")
    
    # Get the latest Excel file
    excel_file = Config.get_latest_excel_file()
    if not excel_file:
        logger.error("no excel files found")
        return []
    
    logger.info(f"using excel file: {excel_file.name}")
    
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
        
        logger.info(f"looking for NSA/SA data for {previous_month_str} and {current_month_str}")
    except Exception as e:
        logger.error(f"error parsing date {date}: {e}")
        return []
    
    # Find the header row and identify columns for both NSA and SA data
    header_info = _find_enhanced_header_columns(df, current_month_str, previous_month_str)
    if not header_info:
        logger.error("could not identify header structure for NSA/SA data")
        return []
    
    # Extract data for each ticker
    results = []
    for ticker in ticker_list:
        ticker_data = _extract_enhanced_ticker_data(df, ticker, header_info, current_month_str, previous_month_str)
        if ticker_data:
            results.append(ticker_data)
    
    logger.info(f"successfully extracted NSA/SA data for {len(results)} out of {len(ticker_list)} categories")
    return results


def _find_enhanced_header_columns(df: pd.DataFrame, current_month: str, previous_month: str) -> Optional[Dict[str, int]]:
    """
    Find column positions for both NSA and SA data in the Excel file.
    
    Args:
        df: Excel data DataFrame
        current_month: Current month string (YYYY-MM)
        previous_month: Previous month string (YYYY-MM)
        
    Returns:
        Dictionary with column mappings for NSA and SA data
    """
    try:
        # Look for the header row with "Expenditure category"
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
        
        # Initialize column mapping
        column_map = {
            'category': None,
            'data_start_row': 6
        }
        
        # Parse current and previous month info
        try:
            current_month_obj = datetime.strptime(current_month, "%Y-%m")
            previous_month_obj = datetime.strptime(previous_month, "%Y-%m")
            
            current_month_name = current_month_obj.strftime("%B").lower()  # e.g., "june"
            current_year = current_month_obj.year
            previous_month_name = previous_month_obj.strftime("%B").lower()  # e.g., "may"
            previous_year = previous_month_obj.year
            
        except Exception as e:
            logger.error(f"error parsing month strings: {e}")
            return None
        
        # Look at header row and subheader row for column identification
        for col_idx in range(len(df.columns)):
            header_cell = str(df.iloc[header_row, col_idx]).lower().replace('\n', ' ') if header_row < len(df) else ""
            subheader_cell = str(df.iloc[header_row + 1, col_idx]).lower().replace('\n', ' ') if header_row + 1 < len(df) else ""
            
            # Expenditure category column
            if "expenditure category" in header_cell:
                column_map['category'] = col_idx
                logger.info(f"category column: {col_idx}")
                continue
            
            # Look for NSA (Unadjusted) INDEX columns - NOT percentage columns
            if "unadjusted indexes" in header_cell:
                # Check for current month
                if (current_month_name[:3] in subheader_cell and str(current_year) in subheader_cell):
                    column_map[f'nsa_{current_month}'] = col_idx
                    logger.info(f"NSA {current_month} index column: {col_idx}")
                # Check for previous month
                elif (previous_month_name[:3] in subheader_cell and str(previous_year) in subheader_cell):
                    column_map[f'nsa_{previous_month}'] = col_idx
                    logger.info(f"NSA {previous_month} index column: {col_idx}")
            
            # Look for SA (Seasonally Adjusted) INDEX columns - NOT percentage columns
            elif "seasonally adjusted indexes" in header_cell:
                # Check for current month
                if (current_month_name[:3] in subheader_cell and str(current_year) in subheader_cell):
                    column_map[f'sa_{current_month}'] = col_idx
                    logger.info(f"SA {current_month} index column: {col_idx}")
                # Check for previous month
                elif (previous_month_name[:3] in subheader_cell and str(previous_year) in subheader_cell):
                    column_map[f'sa_{previous_month}'] = col_idx
                    logger.info(f"SA {previous_month} index column: {col_idx}")
        
        logger.info(f"identified enhanced columns: {column_map}")
        return column_map
    
    except Exception as e:
        logger.error(f"error finding enhanced header columns: {e}")
        return None


def _extract_enhanced_ticker_data(df: pd.DataFrame, ticker: str, header_info: Dict[str, int], 
                                current_month: str, previous_month: str) -> Optional[Dict[str, Any]]:
    """
    Extract NSA and SA data for a specific ticker with dates as column headers.
    
    Args:
        df: Excel data DataFrame
        ticker: Category name to search for
        header_info: Column mapping information
        current_month: Current month string (YYYY-MM)
        previous_month: Previous month string (YYYY-MM)
        
    Returns:
        Dictionary with ticker data in new format
    """
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
        
        # Initialize result with category name
        result = {
            'category': ticker
        }
        
        # Extract NSA values
        nsa_prev_key = f'nsa_{previous_month}'
        nsa_curr_key = f'nsa_{current_month}'
        
        if nsa_prev_key in header_info:
            prev_col = header_info[nsa_prev_key]
            prev_value = df.iloc[matching_row, prev_col]
            result[nsa_prev_key] = _clean_numeric_value(prev_value)
        
        if nsa_curr_key in header_info:
            curr_col = header_info[nsa_curr_key]
            curr_value = df.iloc[matching_row, curr_col]
            result[nsa_curr_key] = _clean_numeric_value(curr_value)
        
        # Extract SA values
        sa_prev_key = f'sa_{previous_month}'
        sa_curr_key = f'sa_{current_month}'
        
        if sa_prev_key in header_info:
            prev_col = header_info[sa_prev_key]
            prev_value = df.iloc[matching_row, prev_col]
            result[sa_prev_key] = _clean_numeric_value(prev_value)
        else:
            # If SA data not available, use NSA data as fallback
            result[sa_prev_key] = result.get(nsa_prev_key)
        
        if sa_curr_key in header_info:
            curr_col = header_info[sa_curr_key]
            curr_value = df.iloc[matching_row, curr_col]
            result[sa_curr_key] = _clean_numeric_value(curr_value)
        else:
            # If SA data not available, use NSA data as fallback
            result[sa_curr_key] = result.get(nsa_curr_key)
        
        logger.info(f"extracted enhanced data for '{ticker}': {result}")
        return result
    
    except Exception as e:
        logger.error(f"error extracting enhanced data for ticker '{ticker}': {e}")
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
        # Convert to string first, then clean
        str_value = str(value).strip()
        
        # Remove common formatting
        str_value = str_value.replace(',', '').replace('%', '')
        
        # Handle empty or dash values
        if str_value in ['', '-', 'N/A', 'n/a', 'nan']:
            return None
        
        return float(str_value)
    
    except (ValueError, TypeError):
        return None


def load_data_to_dataframe(ticker_list: List[str], date: str) -> pd.DataFrame:
    """
    Convenience function that loads enhanced data and returns it as a DataFrame.
    
    Args:
        ticker_list: List of category strings
        date: Date string in format "YYYY-MM"
        
    Returns:
        pandas DataFrame with enhanced data structure
    """
    data_list = load_data(ticker_list, date)
    df = pd.DataFrame(data_list)
    return df


def load_data_long_format(ticker_list: List[str], date: str) -> pd.DataFrame:
    """
    Load BLS data and return in long format with separate rows for each date/adjustment combination.
    
    Args:
        ticker_list: List of category strings that match exactly with Excel sheet
        date: Date string in format "YYYY-MM" (e.g., "2025-06")
        
    Returns:
        pandas DataFrame in long format:
        category   date      index    adjustment
        cpi        2025-06   322.561  nsa
        cpi        2025-06   321.500  sa
        cpi        2025-05   321.465  nsa
        cpi        2025-05   320.580  sa
    """
    # Get the wide format data first
    data_list = load_data(ticker_list, date)
    
    if not data_list:
        return pd.DataFrame(columns=['category', 'date', 'index', 'adjustment'])
    
    # Transform to long format
    long_data = []
    
    for item in data_list:
        category = item['category']
        
        # Extract all the data points
        for key, value in item.items():
            if key == 'category':
                continue
            
            # Parse the key to get adjustment type and date
            if key.startswith('nsa_'):
                adjustment = 'nsa'
                date_str = key.replace('nsa_', '')
            elif key.startswith('sa_'):
                adjustment = 'sa'
                date_str = key.replace('sa_', '')
            else:
                continue
            
            # Add row to long format
            if pd.notna(value) and value is not None:
                long_data.append({
                    'category': category,
                    'date': date_str,
                    'index': value,
                    'adjustment': adjustment
                })
    
    # Create DataFrame and sort by category, date, adjustment
    df = pd.DataFrame(long_data)
    if not df.empty:
        df = df.sort_values(['category', 'date', 'adjustment']).reset_index(drop=True)
    
    return df


def calculate_inflation_rates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate month-over-month inflation rates for both NSA and SA data.
    
    Args:
        df: DataFrame with enhanced BLS data
        
    Returns:
        DataFrame with additional inflation rate columns
    """
    if df.empty:
        return df
    
    df_calc = df.copy()
    
    # Find NSA and SA columns
    nsa_cols = [col for col in df.columns if col.startswith('nsa_')]
    sa_cols = [col for col in df.columns if col.startswith('sa_')]
    
    if len(nsa_cols) >= 2:
        # Sort NSA columns by date
        nsa_cols_sorted = sorted(nsa_cols)
        prev_nsa = nsa_cols_sorted[0]  # Earlier date
        curr_nsa = nsa_cols_sorted[1]  # Later date
        
        df_calc['nsa_mom_change_pct'] = ((df_calc[curr_nsa] - df_calc[prev_nsa]) 
                                        / df_calc[prev_nsa] * 100).round(2)
    
    if len(sa_cols) >= 2:
        # Sort SA columns by date
        sa_cols_sorted = sorted(sa_cols)
        prev_sa = sa_cols_sorted[0]  # Earlier date
        curr_sa = sa_cols_sorted[1]  # Later date
        
        df_calc['sa_mom_change_pct'] = ((df_calc[curr_sa] - df_calc[prev_sa]) 
                                       / df_calc[prev_sa] * 100).round(2)
    
    return df_calc


def example_usage():
    """
    Example of how to use the enhanced load_data function.
    """
    print("Enhanced BLS Data Loading Example")
    print("=" * 50)
    
    # Define categories to load
    ticker_list = [
        "All items",
        "Food", 
        "Energy",
        "Shelter",
        "Transportation"
    ]
    
    # Load data for June 2025
    print(f"Loading NSA/SA data for categories: {ticker_list}")
    data_list = load_data(ticker_list, "2025-06")
    
    if data_list:
        # Convert to DataFrame
        df = pd.DataFrame(data_list)
        print(f"\nSuccessfully loaded data for {len(df)} categories:")
        print(df.to_string(index=False))
        
        # Calculate inflation rates
        df_with_inflation = calculate_inflation_rates(df)
        print(f"\nWith inflation calculations:")
        
        inflation_cols = ['category'] + [col for col in df_with_inflation.columns 
                                       if 'mom_change_pct' in col]
        if len(inflation_cols) > 1:
            print(df_with_inflation[inflation_cols].to_string(index=False))
        
    else:
        print("No data loaded")


if __name__ == "__main__":
    example_usage()