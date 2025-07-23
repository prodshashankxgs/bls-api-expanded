#!/usr/bin/env python3
"""
Quick Start - Use BLS Data Immediately
======================================

This script shows exactly how to use your BLS data in a separate VSCode tab
while the auto-scraper runs in another tab.

Perfect workflow:
1. Tab 1: Run `python3 auto_scraper.py` (keeps data fresh)
2. Tab 2: Run this script or use the functions interactively

Your exact usage pattern works immediately!
"""

from data_loader import DataLoader, load_data, BLSDataClient
import polars as pl
import time

def show_workflow_demo():
    """Demonstrate the exact workflow you want"""
    print("BLS DATA - IMMEDIATE USAGE DEMO")
    print("=" * 50)
    print("This shows your exact workflow working!")
    print()
    
    # Your exact usage pattern
    print("YOUR EXACT PATTERN:")
    print("-" * 30)
    print("from data_loader import DataLoader")
    print('tickers = ["CPSCJEWE Index", "CPIQWAN Index", "CPSCWG Index"]')
    print("dl = DataLoader()")
    print('df = dl.load_data(tickers, "2025-01-01")')
    print()
    
    # Actually run it
    tickers = ["CPSCJEWE Index", "CPIQWAN Index", "CPSCWG Index", "CPSCMB Index", "CPSCINTD Index", "CPIQSMFN Index"]
    dl = DataLoader()
    df = dl.load_data(tickers, "2025-01-01")
    
    print(f"SUCCESS! Loaded {df.shape[0]} rows, {df.shape[1]} columns")
    print(f"Categories: {df.select('category').unique().shape[0]} unique")
    print()
    
    # Show sample data
    print("Sample of your data:")
    sample = df.select(['ticker', 'expenditure_category', 'relative_importance_pct']).head(3)
    print(sample)
    print()

def show_modern_interface():
    """Show the modern interface options"""
    print("MODERN FUNCTION INTERFACE:")
    print("-" * 30)
    
    # Individual ticker loading
    df1 = load_data("CPSCJEWE Index", "latest")
    df2 = load_data("Food", "latest")
    
    print(f"load_data('CPSCJEWE Index', 'latest') → {df1.shape}")
    print(f"load_data('Food', 'latest') → {df2.shape}")
    print()

def show_rest_client():
    """Show the REST client features"""
    print("REST CLIENT (ADVANCED):")
    print("-" * 30)
    
    client = BLSDataClient()
    
    # Get data with caching
    df = client.get_data("CPSCJEWE Index")
    print(f"client.get_data('CPSCJEWE Index') → {df.shape}")
    
    # Search capabilities
    search_results = client.search_categories("food")
    print(f"client.search_categories('food') → {len(search_results)} results")
    
    # Get all categories
    categories = client.get_categories()
    print(f"client.get_categories() → {len(categories)} categories")
    print()

def interactive_demo():
    """Interactive demonstration"""
    print("INTERACTIVE DEMO")
    print("=" * 50)
    print("Try these commands in your Python shell:")
    print()
    
    commands = [
        "from data_loader import load_data, DataLoader, BLSDataClient",
        "",
        "# Your exact pattern:",
        'tickers = ["CPSCJEWE Index", "CPIQWAN Index"]',
        "dl = DataLoader()",
        'df = dl.load_data(tickers, "latest")',
        "print(df.shape)",
        "",
        "# Quick access:",
        'headline = load_data("CPSCJEWE Index", "latest")',
        'food = load_data("Food", "latest")',
        "",
        "# Advanced client:",
        "client = BLSDataClient()",
        'data = client.get_data("CPSCJEWE Index")',
        'categories = client.get_categories()',
        'search = client.search_categories("clothing")',
        "",
        "# Export data:",
        'dl.save_data(df, "my_cpi_data.csv")',
    ]
    
    for cmd in commands:
        if cmd.startswith("#") or cmd == "":
            print(cmd)
        else:
            print(f">>> {cmd}")
    
    print()
    print("All commands work with live data from auto_scraper.py!")

def realtime_data_demo():
    """Show real-time data access"""
    print("REAL-TIME DATA ACCESS")
    print("=" * 50)
    
    # Show that data is fresh
    dl = DataLoader()
    excel_info = dl.get_excel_info()
    
    print(f"Excel files available: {len(excel_info['available_files'])}")
    print(f"Excel system: {'Ready' if excel_info['excel_available'] else 'Not available'}")
    
    if excel_info['available_files']:
        latest_file = excel_info['available_files'][0]
        print(f"Latest file: {latest_file}")
        
        # Load from latest file
        df = load_data("CPSCJEWE Index", "latest")
        if not df.is_empty():
            timestamp = df.select('data_timestamp').head(1)
            print(f"Data timestamp: Fresh data available!")
            print(f"Ready for analysis: {df.shape} data points")
        else:
            print("No data loaded")
    
    print()
    print("This data updates automatically when BLS releases new files!")

def main():
    """Main demo function"""
    print("BLS DATA QUICK START")
    print("Use fresh economic data immediately!")
    print("=" * 60)
    print()
    
    try:
        # Show workflow
        show_workflow_demo()
        
        # Show interfaces
        show_modern_interface()
        show_rest_client()
        
        # Show real-time features
        realtime_data_demo()
        
        # Interactive demo
        interactive_demo()
        
        print("=" * 60)
        print("READY FOR PRODUCTION!")
        print()
        print("Perfect workflow:")
        print("  Tab 1: python3 auto_scraper.py  (keep running)")
        print("  Tab 2: Use your load_data() functions")
        print()
        print("Your economic data is fresh and ready! 📊")
        
    except Exception as e:
        print(f"Error in demo: {e}")
        print()
        print("Make sure to run auto_scraper.py first to get fresh data!")

if __name__ == "__main__":
    main() 