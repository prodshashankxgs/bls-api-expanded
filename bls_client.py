#!/usr/bin/env python3
"""
BLS Data API Client - Simple Module
===================================

Minimal client for accessing BLS data via FastAPI.
Copy this file to any project to access BLS inflation data.

Usage:
    from bls_client import BLSClient
    
    client = BLSClient("http://192.168.1.100:8000")
    df = client.get_data(["All items", "Food"], "2025-06")

Author: Generated with Claude Code
Version: 1.0
"""

import requests
import pandas as pd
from typing import List, Dict, Any, Optional
import warnings

class BLSClient:
    """Simple client for BLS Data API"""
    
    def __init__(self, api_url: str = "http://localhost:8000"):
        """
        Initialize BLS API client
        
        Args:
            api_url: Base URL of the BLS API server
        """
        self.api_url = api_url.rstrip('/')
        self.session = requests.Session()
        
        # Test connection on initialization
        self._test_connection()
    
    def _test_connection(self) -> bool:
        """Test if API server is accessible"""
        try:
            response = self.session.get(f"{self.api_url}/health", timeout=5)
            if response.status_code == 200:
                health_data = response.json()
                print(f"connected to bls api at {self.api_url}")
                print(f"   data available: {health_data.get('data_available', 'unknown')}")
                return True
            else:
                print(f"api responded with status {response.status_code}")
                return False
        except Exception as e:
            print(f"cannot connect to bls api at {self.api_url}")
            print(f"   error: {e}")
            print(f"   make sure the api server is running!")
            return False
    
    def get_categories(self, limit: int = 50) -> List[str]:
        """
        Get available BLS categories
        
        Args:
            limit: Maximum number of categories to return
            
        Returns:
            List of available category names
        """
        try:
            response = self.session.get(f"{self.api_url}/categories", params={"limit": limit})
            response.raise_for_status()
            
            data = response.json()
            categories = data.get("categories", [])
            
            print(f"retrieved {len(categories)} available categories")
            return categories
            
        except Exception as e:
            print(f"error getting categories: {e}")
            return []
    
    def load_data(self, categories: List[str], date: str):
        """
        Load and print BLS data with actual index values and separate NSA/SA columns
        
        Args:
            categories: List of BLS category names
            date: Date in YYYY-MM format
        """
        df = self.get_data(categories, date)
        
        if df is not None:
            # Create processed dataframe with separate NSA/SA columns
            result_df = df[['category']].copy()
            
            # Add NSA columns
            nsa_cols = [col for col in df.columns if col.startswith('nsa_')]
            for nsa_col in nsa_cols:
                date_part = nsa_col.replace('nsa_', '')
                result_df[f'nsa_{date_part}'] = df[nsa_col]
            
            # Add SA columns  
            sa_cols = [col for col in df.columns if col.startswith('sa_')]
            for sa_col in sa_cols:
                date_part = sa_col.replace('sa_', '')
                result_df[f'sa_{date_part}'] = df[sa_col]
            
            print(result_df)
        else:
            print("failed to load data")

    def get_data(self, categories: List[str], date: str) -> Optional[pd.DataFrame]:
        """
        Get BLS data for specified categories and date
        
        Args:
            categories: List of BLS category names (e.g., ["All items", "Food"])
            date: Date in YYYY-MM format (e.g., "2025-06")
            
        Returns:
            DataFrame with BLS data or None if failed
            
        Example:
            df = client.get_data(["All items", "Food", "Energy"], "2025-06")
            print(df[['category', 'nsa_current_month', 'nsa_previous_month']])
        """
        try:
            # Validate inputs
            if not categories:
                raise ValueError("At least one category must be specified")
            
            if len(categories) > 20:
                warnings.warn("More than 20 categories requested, this may be slow")
            
            # Make API request
            payload = {
                "categories": categories,
                "date": date
            }
            
            response = self.session.post(
                f"{self.api_url}/data",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            response.raise_for_status()
            
            # Process response
            result = response.json()
            
            if result.get("success"):
                data = result.get("data", [])
                if data:
                    df = pd.DataFrame(data)
                    print(f"successfully loaded data for {len(df)} categories")
                    return df
                else:
                    print(f"no data found for the specified categories and date {date}")
                    return None
            else:
                print(f"api error: {result.get('message', 'unknown error')}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"network error: {e}")
            return None
        except Exception as e:
            print(f"unexpected error: {e}")
            return None
    
    def get_inflation_analysis(self, categories: List[str], date: str) -> Optional[pd.DataFrame]:
        """
        Get BLS data with calculated month-over-month inflation rates
        
        Args:
            categories: List of BLS category names
            date: Date in YYYY-MM format
            
        Returns:
            DataFrame with inflation analysis or None if failed
        """
        df = self.get_data(categories, date)
        
        if df is not None:
            # Calculate month-over-month change
            df['mom_change_pct'] = ((df['nsa_current_month'] - df['nsa_previous_month']) 
                                   / df['nsa_previous_month'] * 100).round(2)
            
            # Add inflation indicators
            df['inflation_level'] = df['mom_change_pct'].apply(self._get_inflation_level)
            
            print(f"calculated inflation rates for {len(df)} categories")
            
        return df
    
    def _get_inflation_level(self, change_pct: float) -> str:
        """Categorize inflation level"""
        if change_pct > 0.5:
            return "High"
        elif change_pct > 0.2:
            return "Moderate"
        elif change_pct > 0:
            return "Low"
        elif change_pct == 0:
            return "Stable"
        else:
            return "Deflation"
    
    def get_status(self) -> Dict[str, Any]:
        """Get API status information"""
        try:
            response = self.session.get(f"{self.api_url}/status")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def download_latest_data(self) -> Dict[str, Any]:
        """Trigger download of latest BLS data on the server"""
        try:
            response = self.session.get(f"{self.api_url}/download")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def quick_analysis(self, date: str = "2025-06") -> Optional[pd.DataFrame]:
        """
        Quick inflation analysis with common categories
        
        Args:
            date: Date to analyze (default: "2025-06")
            
        Returns:
            DataFrame with analysis results
        """
        common_categories = [
            "All items",
            "Food",
            "Energy",
            "Shelter",
            "Transportation",
            "Medical care"
        ]
        
        print(f"running quick analysis for {date}")
        return self.get_inflation_analysis(common_categories, date)

# Convenience functions for direct usage
def connect_to_bls_api(api_url: str = "http://localhost:8000") -> BLSClient:
    """Create and return a BLS API client"""
    return BLSClient(api_url)

def get_bls_data(api_url: str, categories: List[str], date: str) -> Optional[pd.DataFrame]:
    """Direct function to get BLS data"""
    client = BLSClient(api_url)
    return client.get_data(categories, date)

# Example usage
if __name__ == "__main__":
    # Test the client
    print("testing bls api client")
    print("=" * 40)
    
    # Create client (adjust URL as needed)
    client = BLSClient("http://localhost:8000")
    
    # Quick test
    df = client.quick_analysis("2025-06")
    
    if df is not None:
        print("\nactual index values:")
        # Show actual index values, not calculated percentages
        nsa_cols = [col for col in df.columns if col.startswith('nsa_') and 'mom' not in col]
        sa_cols = [col for col in df.columns if col.startswith('sa_') and 'mom' not in col]
        display_cols = ['category'] + nsa_cols[:2] + sa_cols[:2]
        available_cols = [col for col in display_cols if col in df.columns]
        print(df[available_cols].to_string(index=False))
    else:
        print("test failed - make sure the api server is running")