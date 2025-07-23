#!/usr/bin/env python3
"""
BLS Economic Data Scraper - Comprehensive Examples
==================================================

This file contains all usage examples for the BLS Data Scraper API.
Consolidates basic_usage.py, excel_usage.py, and rest_api_example.py.

Run this file to see all examples, or import specific functions:
    python3 examples.py
    
    from examples import basic_example, excel_example, rest_api_example
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from data_loader import DataLoader, load_data, BLSDataClient
import polars as pl
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def basic_example():
    """
    Basic usage example - demonstrates the original DataLoader interface
    """
    print("BASIC USAGE EXAMPLE")
    print("=" * 50)
    print("Demonstrates the backward-compatible DataLoader interface")
    print()
    
    try:
        # Initialize the data loader
        dl = DataLoader()
        
        # Check if system is ready
        if not dl.health_check():
            print("System not fully ready, but will work with available data")
        else:
            print("System is ready")
        
        print("\nLoading economic indicators...")
        
        # Load multiple indicators
        indicators = ["CPSCJEWE Index", "CPIQWAN Index", "Food", "Energy"]
        df = dl.load_data(indicators, "latest")
        
        if df.is_empty():
            print("No data loaded!")
            return
        
        print(f"Successfully loaded {len(df)} data points")
        print(f"Indicators: {len(df['ticker'].unique())} different tickers")
        print(f"Data shape: {df.shape}")
        
        print("Sample Data:")
        sample = df.select(['ticker', 'expenditure_category', 'relative_importance_pct']).head(5)
        print(sample)
        
        # Show available indicators
        available = dl.get_available_indicators()
        print(f"Total available indicators: {len(available)}")
        
        # Export example
        output_file = "basic_example_output.csv"
        dl.save_data(df, output_file)
        print(f"Data saved to: {output_file}")
        
        return df
        
    except Exception as e:
        print(f"Error in basic example: {e}")
        return None

def excel_example():
    """
    Excel-based data loading example
    """
    print("EXCEL DATA LOADING EXAMPLE")
    print("=" * 50)
    print("Demonstrates Excel-based CPI data loading with fallbacks")
    print()
    
    try:
        # Initialize with Excel support
        dl = DataLoader(enable_excel=True)
        
        # Check Excel status
        excel_info = dl.get_excel_info()
        print(f"Excel system: {'Available' if excel_info['excel_available'] else 'Not available'}")
        print(f"Downloaded files: {len(excel_info['available_files'])}")
        
        if excel_info['available_files']:
            print("   Files:")
            for file in excel_info['available_files']:
                print(f"      - {file}")
        
        print("Loading CPI data from Excel...")
        
        # Load CPI data (tries Excel first, falls back to API/sample)
        df = dl.load_data_with_excel_fallback('CPSCJEWE Index', '2025-06', prefer_excel=True)
        
        if df.is_empty():
            print("No data loaded!")
            return
        
        print(f"Loaded {len(df)} CPI data points")
        
        # Show Excel-specific data
        if 'data_timestamp' in df.columns:
            print("Data freshness:")
            for row in df.head(3).iter_rows(named=True):
                category = row.get('expenditure_category', 'N/A')
                timestamp = row.get('data_timestamp', 'N/A')
                print(f"   • {category}: {timestamp}")
        
        # Show detailed CPI breakdown
        print("CPI Categories Available:")
        if 'expenditure_category' in df.columns:
            categories = df.select('expenditure_category').unique().to_series().to_list()
            for i, category in enumerate(categories[:10]):
                print(f"   {i+1:2d}. {category}")
            if len(categories) > 10:
                print(f"       ... and {len(categories) - 10} more")
        
        return df
        
    except Exception as e:
        print(f"Error in Excel example: {e}")
        return None

def rest_api_example():
    """
    REST-like client interface example
    """
    print("REST-LIKE CLIENT EXAMPLE")
    print("=" * 50)
    print("Demonstrates the advanced BLSDataClient interface")
    print()
    
    try:
        # Initialize client
        client = BLSDataClient(cache_ttl=3600)
        
        print("Client Features Demo:")
        
        # 1. Basic data retrieval
        df = client.get_data("CPSCJEWE Index", date="latest", use_cache=True)
        print(f"Data retrieval: {df.shape}")
        
        # 2. Category exploration
        categories = client.get_categories()
        print(f"Total categories: {len(categories)}")
        
        # Show category hierarchy
        level_counts = {}
        for cat in categories:
            level = cat.get('level', 0)
            level_counts[level] = level_counts.get(level, 0) + 1
        
        print("Category hierarchy:")
        for level in sorted(level_counts.keys()):
            print(f"      Level {level}: {level_counts[level]} categories")
        
        # 3. Search functionality
        search_results = client.search_categories("food")
        print(f"Search 'food': {len(search_results)} results")
        
        if search_results:
            print("      Top matches:")
            for result in search_results[:3]:
                print(f"         • {result['description']} (Score: {result['relevance_score']:.1f})")
        
        # 4. Weights analysis
        weights = client.get_weights()
        print(f"Weights data: {weights.shape}")
        
        if not weights.is_empty() and 'weight_numeric' in weights.columns:
            print("      Top weighted categories:")
            top_weights = weights.head(5)
            for row in top_weights.iter_rows(named=True):
                category = row.get('expenditure_category', 'N/A')[:40]
                weight = row.get('weight_numeric', 0)
                print(f"         • {category:<40} {weight:>6.2f}%")
        
        # 5. Complete dataset
        complete_data = client.get_complete_dataset()
        print(f"Complete dataset: {complete_data.shape}")
        
        # 6. Time series (simulated)
        timeseries = client.get_time_series("CPSCJEWE Index", "2024-01", "2025-06")
        print(f"Time series: {timeseries.shape}")
        
        # 7. Cache management
        print("Cache management:")
        print("      Cache hits and misses tracked automatically")
        client.clear_cache()
        print("      Cache cleared for fresh data")
        
        return client
        
    except Exception as e:
        print(f"Error in REST API example: {e}")
        return None

def modern_functions_example():
    """
    Modern function-based interface example
    """
    print("\n⚡ MODERN FUNCTIONS EXAMPLE")
    print("=" * 50)
    print("Demonstrates the streamlined function interface")
    print()
    
    try:
        # Individual ticker loading
        print("Individual ticker loading:")
        
        tickers = ["CPSCJEWE Index", "Food", "Energy", "Shelter"]
        results = {}
        
        for ticker in tickers:
            df = load_data(ticker, "latest")
            results[ticker] = df
            source = "Excel" if not df.is_empty() and 'unadj_index_jun2025' in df.columns else "API/Sample"
            print(f"   • {ticker:<20} → {df.shape} ({source})")
        
        # Show data combination
        print("Combining multiple datasets:")
        all_data = []
        for ticker, df in results.items():
            if not df.is_empty():
                all_data.append(df)
        
        if all_data:
            combined = pl.concat(all_data)
            print(f"Combined dataset: {combined.shape}")
            
            # Show variety of data sources
            if 'category' in combined.columns:
                categories = combined.select('category').unique().to_series().to_list()
                print(f"Categories represented: {len(categories)}")
                for cat in categories:
                    count = combined.filter(pl.col('category') == cat).shape[0]
                    print(f"      - {cat}: {count} data points")
        
        return results
        
    except Exception as e:
        print(f"Error in modern functions example: {e}")
        return None

def performance_example():
    """
    Performance and optimization example
    """
    print("\n⚡ PERFORMANCE & OPTIMIZATION EXAMPLE")
    print("=" * 50)
    print("Demonstrates performance features and optimizations")
    print()
    
    try:
        import time
        
        # Caching performance test
        print("Caching Performance Test:")
        client = BLSDataClient(cache_ttl=3600)
        
        # First call (cache miss)
        start_time = time.time()
        df1 = client.get_data("CPSCJEWE Index", use_cache=True)
        first_call_time = time.time() - start_time
        print(f"   First call (cache miss): {first_call_time:.3f}s → {df1.shape}")
        
        # Second call (cache hit)
        start_time = time.time()
        df2 = client.get_data("CPSCJEWE Index", use_cache=True)
        second_call_time = time.time() - start_time
        print(f"   Second call (cache hit): {second_call_time:.3f}s → {df2.shape}")
        
        if second_call_time > 0:
            speedup = first_call_time / second_call_time
            print(f"Speedup: {speedup:.1f}x faster with cache")
        
        # Bulk loading performance
        print("Bulk Loading Performance:")
        start_time = time.time()
        dl = DataLoader()
        tickers = ["CPSCJEWE Index", "CPIQWAN Index", "Food", "Energy", "Shelter"]
        bulk_df = dl.load_data(tickers, "latest")
        bulk_time = time.time() - start_time
        print(f"   Bulk load {len(tickers)} tickers: {bulk_time:.3f}s → {bulk_df.shape}")
        
        # Memory efficiency with Polars
        print("Memory Efficiency:")
        if not bulk_df.is_empty():
            memory_usage = bulk_df.estimated_size("mb")
            print(f"   Dataset memory usage: {memory_usage:.2f} MB")
            print(f"   Rows per MB: {bulk_df.shape[0] / max(memory_usage, 0.001):.0f}")
        
        print("Using Polars for optimal memory performance")
        
    except Exception as e:
        print(f"Error in performance example: {e}")

def integration_example():
    """
    Integration with auto-scraper example
    """
    print("AUTO-SCRAPER INTEGRATION EXAMPLE")
    print("=" * 50)
    print("Shows how data updates automatically with auto_scraper.py")
    print()
    
    try:
        dl = DataLoader()
        
        # Check for fresh data
        excel_info = dl.get_excel_info()
        print("Current Data Status:")
        print(f"   Excel files: {len(excel_info['available_files'])}")
        
        if excel_info['available_files']:
            latest_file = excel_info['available_files'][0]
            file_path = Path("data_sheet") / latest_file
            
            if file_path.exists():
                import os
                from datetime import datetime
                
                file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                age = datetime.now() - file_time
                
                print(f"   Latest file: {latest_file}")
                print(f"   File age: {age.total_seconds() / 3600:.1f} hours")
                print(f"   File size: {file_path.stat().st_size / 1024:.1f} KB")
        
        # Load data to show it's working
        df = load_data("CPSCJEWE Index", "latest")
        if not df.is_empty():
            print(f"Data accessible: {df.shape}")
            print("Ready for analysis")
        
        print("Integration Workflow:")
        print("   1. Run: python3 auto_scraper.py (in Tab 1)")
        print("   2. Use: load_data() functions (in Tab 2)")
        print("   3. Data updates automatically when BLS releases new files")
        print("   4. Your analysis code doesn't need to change!")
        
    except Exception as e:
        print(f"Error in integration example: {e}")

def main():
    """
    Run all examples
    """
    print("BLS ECONOMIC DATA SCRAPER - ALL EXAMPLES")
    print("=" * 70)
    print("Comprehensive demonstration of all features and interfaces")
    print()
    
    try:
        # Run all examples
        basic_df = basic_example()
        excel_df = excel_example()
        client = rest_api_example()
        modern_results = modern_functions_example()
        performance_example()
        integration_example()
        
        # Summary
        print("ALL EXAMPLES COMPLETED!")
        print("=" * 70)
        print("Basic DataLoader interface")
        print("Excel data loading with fallbacks")
        print("REST-like client with advanced features")
        print("Modern function interface")
        print("Performance optimizations")
        print("Auto-scraper integration")
        print()
        print("Your BLS data pipeline is ready for production!")
        print()
        print("Next steps:")
        print("   • Run auto_scraper.py for automatic updates")
        print("   • Use load_data() functions in your analysis")
        print("   • Explore BLSDataClient for advanced features")
        
    except Exception as e:
        print(f"Error running examples: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 