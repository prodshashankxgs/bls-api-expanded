#!/usr/bin/env python3
"""
BLS Data API Client - Final Production Version
==============================================

Minimal client that returns BLS data in the exact format you want:
category | date | index | adjustment

Usage:
    from bls_client_final import load_data, get_all_tickers
    
    # Get all tickers
    all_tickers = get_all_tickers()
    
    # Load data in your desired format
    df = load_data(all_tickers, "2025-06")
    print(df)

Author: Generated with Claude Code
Version: Final
"""

import requests
import pandas as pd
from typing import List, Optional
import warnings


class BLSClient:
    """Final BLS API client that returns data in your desired format"""
    
    def __init__(self, api_url: str = "http://localhost:8000"):
        self.api_url = api_url.rstrip('/')
        self.session = requests.Session()
        self._test_connection()
    
    def _test_connection(self) -> bool:
        """Test if API server is accessible"""
        try:
            response = self.session.get(f"{self.api_url}/health", timeout=5)
            if response.status_code == 200:
                health_data = response.json()
                print(f"Connected to BLS API at {self.api_url}")
                print(f"   Data available: {health_data.get('data_available', 'unknown')}")
                return True
            else:
                print(f"API responded with status {response.status_code}")
                return False
        except Exception as e:
            print(f"Cannot connect to BLS API at {self.api_url}")
            print(f"   Error: {e}")
            print(f"   Make sure the API server is running!")
            return False
    
    def get_all_tickers(self) -> List[str]:
        """Get ALL available tickers from the API"""
        try:
            response = self.session.get(f"{self.api_url}/categories", params={"limit": 200})
            response.raise_for_status()
            
            data = response.json()
            tickers = data.get("categories", [])
            
            print(f"Retrieved {len(tickers)} available tickers")
            return tickers
            
        except Exception as e:
            print(f"Error getting tickers: {e}")
            return []

    def get_data(self, ticker: List[str], date: str) -> Optional[pd.DataFrame]:
        """
        Get BLS data in your desired format: category | date | index | adjustment
        
        Args:
            ticker: List of BLS ticker names
            date: Date in YYYY-MM format (e.g., "2025-06")
            
        Returns:
            DataFrame in your desired format or None if failed
        """
        try:
            if not ticker:
                raise ValueError("At least one ticker must be specified")
            
            if len(ticker) > 200:
                warnings.warn("More than 200 tickers requested, this may be slow")
            
            # Make API request for long format
            payload = {"categories": ticker, "date": date}
            params = {"long_format": "true"}
            
            response = self.session.post(
                f"{self.api_url}/data",
                json=payload,
                params=params,
                headers={"Content-Type": "application/json"},
                timeout=60  # Longer timeout for large requests
            )
            response.raise_for_status()
            
            result = response.json()
            
            if result.get("success"):
                data = result.get("data", [])
                if data:
                    df = pd.DataFrame(data)
                    print(f"Successfully loaded data for {len(ticker)} tickers")
                    print(f"   Returned {len(df)} rows in your desired format")
                    return df
                else:
                    print(f"No data found for date {date}")
                    return None
            else:
                print(f"API error: {result.get('message', 'unknown error')}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"Network error: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None


# Global client instance
_default_client = None


def load_data(ticker: List[str], date: str, api_url: str = "http://localhost:8000") -> Optional[pd.DataFrame]:
    """
    Load BLS data in your exact desired format
    
    Args:
        ticker: List of BLS ticker names (get from get_all_tickers())
        date: Date in YYYY-MM format (e.g., "2025-06")
        api_url: API server URL
        
    Returns:
        DataFrame in format:
        category   date      index    adjustment
        All items  2025-06   322.561  nsa
        All items  2025-06   321.500  sa  
        All items  2025-05   321.465  nsa
        All items  2025-05   320.580  sa
        Food       2025-06   339.498  nsa
        Food       2025-06   339.498  sa
        ...
    """
    global _default_client
    
    if _default_client is None or _default_client.api_url != api_url.rstrip('/'):
        _default_client = BLSClient(api_url)
    
    return _default_client.get_data(ticker, date)


def get_all_tickers(api_url: str = "http://localhost:8000") -> List[str]:
    """
    Get all available tickers from the API
    
    Args:
        api_url: API server URL
        
    Returns:
        List of all ticker names
    """
    global _default_client
    
    if _default_client is None or _default_client.api_url != api_url.rstrip('/'):
        _default_client = BLSClient(api_url)
    
    return _default_client.get_all_tickers()


if __name__ == "__main__":
    print("Testing Final BLS Client")
    print("=" * 40)
    
    # Get all tickers
    print("1. Getting all available tickers...")
    all_tickers = get_all_tickers()
    print(f"   Found {len(all_tickers)} tickers")
    
    # Test with a subset first
    print("\n2. Testing with subset of tickers...")
    test_tickers = ["All items", "Food", "Energy"]
    df = load_data(test_tickers, "2025-06")
    
    if df is not None:
        print(f"   Success! Shape: {df.shape}")
        print(f"   Columns: {list(df.columns)}")
        print("\n   Sample data:")
        print(df.head())
        
        print(f"\n3. Testing with ALL {len(all_tickers)} tickers...")
        df_all = load_data(all_tickers, "2025-06")
        if df_all is not None:
            print(f"   ALL tickers loaded! Shape: {df_all.shape}")
            print(f"   Categories: {df_all['category'].nunique()}")
            print(f"   Total rows: {len(df_all)}")
        else:
            print("   Failed to load all tickers")
    else:
        print("   Test failed")
    
    print("\n" + "=" * 40)
    print("✨ Test complete!") 