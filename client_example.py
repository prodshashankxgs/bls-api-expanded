#!/usr/bin/env python3
"""
BLS Data API Client Example
===========================

Example client for consuming the BLS Data API from any system.
Your colleague can use this code on Windows, Mac, or Linux.

Usage:
    python client_example.py

Requirements:
    pip install requests pandas matplotlib

API Server should be running at: http://localhost:8000
"""

import requests
import pandas as pd
import json
from typing import List, Dict, Any, Optional
import time

class BLSDataClient:
    """Simple client for BLS Data API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize the client
        
        Args:
            base_url: Base URL of the BLS API server
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        
        # Test connection
        self._test_connection()
    
    def _test_connection(self):
        """Test if the API server is reachable"""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                print(f"✅ Connected to BLS API at {self.base_url}")
            else:
                print(f"⚠️  API server responded with status {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"❌ Cannot connect to API server at {self.base_url}")
            print(f"   Error: {e}")
            print(f"   Make sure the API server is running with: python api.py")
    
    def get_health(self) -> Dict:
        """Get API health status"""
        try:
            response = self.session.get(f"{self.base_url}/health")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}
    
    def get_categories(self, limit: int = 50) -> List[str]:
        """
        Get available BLS categories
        
        Args:
            limit: Maximum number of categories to return
            
        Returns:
            List of category names
        """
        try:
            response = self.session.get(f"{self.base_url}/categories", params={"limit": limit})
            response.raise_for_status()
            data = response.json()
            return data.get("categories", [])
        except requests.exceptions.RequestException as e:
            print(f"Error getting categories: {e}")
            return []
    
    def load_data(self, categories: List[str], date: str) -> Optional[pd.DataFrame]:
        """
        Load BLS data for specified categories and date
        
        Args:
            categories: List of category names
            date: Date in YYYY-MM format
            
        Returns:
            DataFrame with the data or None if failed
        """
        try:
            # Method 1: POST request (recommended)
            payload = {
                "categories": categories,
                "date": date
            }
            
            response = self.session.post(
                f"{self.base_url}/data",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            
            result = response.json()
            
            if result.get("success"):
                data = result.get("data", [])
                if data:
                    df = pd.DataFrame(data)
                    print(f"✅ Loaded data for {len(df)} categories")
                    return df
                else:
                    print("⚠️  No data returned from API")
                    return None
            else:
                print(f"❌ API returned error: {result.get('message', 'Unknown error')}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            return None
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return None
    
    def load_data_get(self, categories: List[str], date: str) -> Optional[pd.DataFrame]:
        """
        Load BLS data using GET request (alternative method)
        
        Args:
            categories: List of category names
            date: Date in YYYY-MM format
            
        Returns:
            DataFrame with the data or None if failed
        """
        try:
            # Join categories with commas
            categories_str = ",".join(categories)
            
            response = self.session.get(f"{self.base_url}/data/{categories_str}/{date}")
            response.raise_for_status()
            
            result = response.json()
            
            if result.get("success"):
                data = result.get("data", [])
                if data:
                    return pd.DataFrame(data)
                else:
                    print("⚠️  No data returned from API")
                    return None
            else:
                print(f"❌ API returned error: {result.get('message', 'Unknown error')}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            return None
    
    def get_status(self) -> Dict:
        """Get detailed API status"""
        try:
            response = self.session.get(f"{self.base_url}/status")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}
    
    def download_latest_data(self) -> Dict:
        """Trigger download of latest BLS data"""
        try:
            response = self.session.get(f"{self.base_url}/download")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

def analyze_inflation_data(client: BLSDataClient, target_date: str = "2025-06"):
    """
    Example analysis using the BLS API client
    
    Args:
        client: BLS API client instance
        target_date: Date to analyze (YYYY-MM format)
    """
    print(f"\n🏛️  BLS Inflation Analysis for {target_date}")
    print("=" * 60)
    
    # Define categories to analyze
    categories = [
        "All items",
        "Food",
        "Energy", 
        "Shelter",
        "Medical care",
        "Transportation"
    ]
    
    print(f"📊 Analyzing {len(categories)} categories:")
    for i, cat in enumerate(categories, 1):
        print(f"   {i}. {cat}")
    
    # Load data from API
    print(f"\n📡 Loading data from API...")
    df = client.load_data(categories, target_date)
    
    if df is None:
        print("❌ Failed to load data from API")
        return
    
    # Calculate month-over-month changes
    df['mom_change_pct'] = ((df['nsa_current_month'] - df['nsa_previous_month']) 
                           / df['nsa_previous_month'] * 100).round(2)
    
    # Display results
    print(f"\n📈 Month-over-Month Inflation Results:")
    print("-" * 60)
    
    for _, row in df.iterrows():
        category = row['category']
        prev_val = row['nsa_previous_month']
        curr_val = row['nsa_current_month'] 
        change = row['mom_change_pct']
        
        # Add visual indicators
        if change > 0.5:
            indicator = "🔴"  # High inflation
        elif change > 0:
            indicator = "🟡"  # Moderate inflation
        elif change == 0:
            indicator = "⚪"  # No change
        else:
            indicator = "🟢"  # Deflation
        
        print(f"{indicator} {category:15s}: {prev_val:6.1f} → {curr_val:6.1f} ({change:+.2f}%)")
    
    # Summary statistics
    avg_inflation = df['mom_change_pct'].mean()
    max_inflation = df['mom_change_pct'].max()
    min_inflation = df['mom_change_pct'].min()
    
    print("-" * 60)
    print(f"📊 Summary Statistics:")
    print(f"   Average inflation: {avg_inflation:+.2f}%")
    print(f"   Highest category:  {max_inflation:+.2f}%")
    print(f"   Lowest category:   {min_inflation:+.2f}%")
    
    return df

def main():
    """Main example function"""
    print("🏛️  BLS Data API Client Example")
    print("=" * 50)
    print("Bureau of Labor Statistics Data Analysis")
    print()
    
    # Create API client
    client = BLSDataClient()
    
    # Check API health
    print("\n🏥 Checking API Health...")
    health = client.get_health()
    if 'error' not in health:
        print(f"   Status: {health.get('status', 'unknown')}")
        print(f"   Data available: {health.get('data_available', False)}")
        print(f"   Latest file: {health.get('latest_file', 'None')}")
        print(f"   Categories: {health.get('categories_count', 0)}")
    else:
        print(f"   Error: {health['error']}")
        return
    
    # Get available categories
    print("\n📋 Available Categories (sample):")
    categories = client.get_categories(10)
    for i, cat in enumerate(categories[:10], 1):
        print(f"   {i:2d}. {cat}")
    
    # Run analysis
    df = analyze_inflation_data(client, "2025-06")
    
    # Optional: Save results to CSV
    if df is not None:
        output_file = f"bls_inflation_analysis_{int(time.time())}.csv"
        df.to_csv(output_file, index=False)
        print(f"\n💾 Results saved to: {output_file}")
    
    print(f"\n✨ Analysis complete!")

def quick_example():
    """Quick example for immediate testing"""
    print("🚀 Quick BLS API Test")
    print("-" * 30)
    
    # Connect to API
    client = BLSDataClient()
    
    # Simple data request
    categories = ["All items", "Food", "Energy"]
    data = client.load_data(categories, "2025-06")
    
    if data is not None:
        print(f"✅ Successfully loaded {len(data)} categories")
        print("\nData preview:")
        print(data[['category', 'nsa_previous_month', 'nsa_current_month']].to_string())
    else:
        print("❌ Failed to load data")

if __name__ == "__main__":
    # Run the main example
    main()
    
    # Uncomment below for quick test
    # quick_example()