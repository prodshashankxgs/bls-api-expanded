#!/usr/bin/env python3
"""
BLS Scraper API - Integration Examples

This file contains practical examples of how to integrate the BLS API
into your own Python projects for various use cases.

Run this file to see all examples in action:
    python example_integrations.py
"""

import sys
import os
from datetime import datetime, timedelta
import json

# Add the app directory to Python path for imports
if 'app' not in sys.path:
    sys.path.append('.')

try:
    from app.fast_bls_api import load_data as load_cached
    from app.fast_bls_api import FastBLSAPI
    from app.live_bls_scraper import load_data as load_live
    from app.live_bls_scraper import LiveBLSScraper
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running from the project root directory")
    sys.exit(1)

def example_1_basic_usage():
    """Example 1: Basic data loading for quick analysis"""
    print("=" * 60)
    print("📊 Example 1: Basic Economic Data Loading")
    print("=" * 60)
    
    # Get recent CPI data
    print("Loading CPI data...")
    cpi_data = load_cached('cpi', '2024')
    
    if cpi_data:
        latest = cpi_data[0]
        print(f"✅ Latest CPI: {latest['value']} ({latest['date']})")
        print(f"📈 Found {len(cpi_data)} data points for 2024")
        
        # Calculate month-over-month change
        if len(cpi_data) >= 2:
            prev_month = cpi_data[1]
            mom_change = ((latest['value'] - prev_month['value']) / prev_month['value']) * 100
            print(f"📊 Month-over-month change: {mom_change:.2f}%")
    else:
        print("❌ Failed to load CPI data")
    
    print()

def example_2_multi_indicator_analysis():
    """Example 2: Analyze multiple economic indicators together"""
    print("=" * 60)
    print("🔄 Example 2: Multi-Indicator Economic Analysis")
    print("=" * 60)
    
    # Load multiple indicators
    indicators = ['cpi', 'cpi_core', 'ppi', 'unemployment']
    
    api = FastBLSAPI()
    data = api.load_multiple(indicators, '2024')
    
    print("Economic Indicators Summary (2024):")
    print("-" * 40)
    
    for ticker, series_data in data.items():
        if series_data:
            latest = series_data[0]
            print(f"{ticker.upper():12}: {latest['value']:8.1f} ({latest['date']})")
        else:
            print(f"{ticker.upper():12}: No data available")
    
    print()

def example_3_inflation_tracker():
    """Example 3: Real-time inflation tracking system"""
    print("=" * 60)
    print("🎯 Example 3: Inflation Tracking System")
    print("=" * 60)
    
    def calculate_inflation_metrics(cpi_data):
        """Calculate various inflation metrics"""
        if len(cpi_data) < 13:  # Need 13 months for YoY calculation
            return None
        
        latest = cpi_data[0]
        prev_month = cpi_data[1]
        year_ago = cpi_data[12]  # 12 months ago
        
        # Month-over-month (annualized)
        mom_rate = ((latest['value'] / prev_month['value']) ** 12 - 1) * 100
        
        # Year-over-year
        yoy_rate = ((latest['value'] / year_ago['value']) - 1) * 100
        
        return {
            'current_cpi': latest['value'],
            'date': latest['date'],
            'mom_annualized': mom_rate,
            'yoy_rate': yoy_rate
        }
    
    # Get comprehensive CPI data
    cpi_data = load_cached('cpi', '2022-2024')
    
    if cpi_data:
        metrics = calculate_inflation_metrics(cpi_data)
        
        if metrics:
            print(f"📈 Current CPI: {metrics['current_cpi']:.1f} ({metrics['date']})")
            print(f"📊 Month-over-Month (annualized): {metrics['mom_annualized']:+.2f}%")
            print(f"📉 Year-over-Year: {metrics['yoy_rate']:+.2f}%")
            
            # Trading signal logic
            if metrics['yoy_rate'] > 3.0:
                signal = "🔴 HIGH INFLATION ALERT"
            elif metrics['yoy_rate'] < 1.0:
                signal = "🟡 LOW INFLATION WARNING"
            else:
                signal = "🟢 INFLATION NORMAL"
            
            print(f"🎯 Trading Signal: {signal}")
        else:
            print("❌ Insufficient data for inflation calculation")
    else:
        print("❌ Failed to load CPI data")
    
    print()

def example_4_fresh_vs_cached_comparison():
    """Example 4: Compare fresh vs cached data performance"""
    print("=" * 60)
    print("⚡ Example 4: Fresh vs Cached Data Performance")
    print("=" * 60)
    
    import time
    
    # Test cached data speed
    start_time = time.time()
    cached_data = load_cached('cpi', '2024')
    cached_time = (time.time() - start_time) * 1000
    
    # Test live scraping speed
    start_time = time.time()
    live_data = load_live('cpi', '2024')
    live_time = (time.time() - start_time) * 1000
    
    print("Performance Comparison:")
    print("-" * 30)
    print(f"Cached API:    {cached_time:6.1f}ms ({len(cached_data) if cached_data else 0} points)")
    print(f"Live Scraper:  {live_time:6.1f}ms ({len(live_data) if live_data else 0} points)")
    print(f"Speed ratio:   {live_time/cached_time:.1f}x slower for live data")
    
    # Data freshness comparison
    if cached_data and live_data:
        cached_latest = cached_data[0]['date']
        live_latest = live_data[0]['date']
        
        print(f"\nData Freshness:")
        print(f"Cached data:   {cached_latest}")
        print(f"Live data:     {live_latest}")
        
        if hasattr(live_data[0], 'scraped_at'):
            print(f"Live scraped:  {live_data[0]['scraped_at']}")
    
    print()

def example_5_standardized_format():
    """Example 5: Using professional standardized format"""
    print("=" * 60)
    print("🏛️ Example 5: Professional Standardized Format")
    print("=" * 60)
    
        # Get data in professional format
    response = load_cached('cpi', '2024', standardized=True)
    
    if response and isinstance(response, dict) and response.get('success'):
        # Display response structure
        print("Response Structure:")
        print("-" * 20)
        print(f"Success: {response.get('success')}")
        print(f"Data points: {len(response.get('data', []))}")
        series_info = response.get('series', {})
        print(f"Series ID: {series_info.get('id')}")
        print(f"Series name: {series_info.get('name')}")
        metadata = response.get('metadata', {})
        print(f"Data quality: {metadata.get('quality')}")
        print(f"API version: {metadata.get('api_version')}")
        print(f"Response time: {metadata.get('latency_ms')}ms")
        
        # Show latest data point
        data_points = response.get('data', [])
        if data_points:
            latest = data_points[0]
            print(f"\nLatest Data Point:")
            print(f"Date: {latest.get('date')}")
            print(f"Value: {latest.get('value')}")
            print(f"Units: {latest.get('units')}")
            print(f"Status: {latest.get('revision_status')}")
    else:
        print("❌ Failed to get standardized data")
    
    print()

def example_6_error_handling():
    """Example 6: Proper error handling"""
    print("=" * 60)
    print("🛡️ Example 6: Error Handling Best Practices")
    print("=" * 60)
    
    def safe_load_data(ticker, date, use_live=False):
        """Safely load data with comprehensive error handling"""
        try:
            # Choose API based on requirements
            load_func = load_live if use_live else load_cached
            data = load_func(ticker, date, standardized=True)
            
            if not data:
                print(f"⚠️ No data returned for {ticker}")
                return None
            
            if isinstance(data, dict) and not data.get('success'):
                error = data.get('error', {})
                print(f"❌ API Error: {error.get('message', 'Unknown error')}")
                return None
            
            return data
            
        except Exception as e:
            print(f"❌ Exception loading {ticker}: {e}")
            return None
    
    # Test with valid ticker
    print("Testing valid ticker (cpi)...")
    valid_data = safe_load_data('cpi', '2024')
    if valid_data:
        print("✅ Successfully loaded CPI data")
    
    # Test with invalid ticker
    print("\nTesting invalid ticker (xyz)...")
    invalid_data = safe_load_data('xyz', '2024')
    if not invalid_data:
        print("✅ Properly handled invalid ticker")
    
    # Test with invalid date
    print("\nTesting invalid date format...")
    invalid_date = safe_load_data('cpi', 'invalid-date-format')
    if not invalid_date:
        print("✅ Properly handled invalid date")
    
    print()

def example_7_pandas_integration():
    """Example 7: Integration with pandas for analysis"""
    print("=" * 60)
    print("🐼 Example 7: Pandas DataFrame Integration")
    print("=" * 60)
    
    try:
        import pandas as pd
        
        # Load multiple economic indicators
        indicators = {
            'CPI': load_cached('cpi', '2020-2024'),
            'Core_CPI': load_cached('cpi_core', '2020-2024'),
            'PPI': load_cached('ppi', '2020-2024'),
            'Unemployment': load_cached('unemployment', '2020-2024')
        }
        
        # Convert to DataFrames and combine
        dfs = []
        for name, data in indicators.items():
            if data:
                df = pd.DataFrame(data)
                df['date'] = pd.to_datetime(df['date'])
                df = df[['date', 'value']].rename(columns={'value': name})
                df = df.set_index('date').sort_index()
                dfs.append(df)
        
        if dfs:
            # Combine all indicators
            combined_df = pd.concat(dfs, axis=1)
            
            print("Economic Indicators DataFrame:")
            print(combined_df.tail())
            
            # Calculate correlations
            correlations = combined_df.corr()
            print(f"\nCorrelation between CPI and PPI: {correlations.loc['CPI', 'PPI']:.3f}")
            
            # Calculate year-over-year changes
            yoy_changes = combined_df.pct_change(periods=12) * 100
            print(f"\nLatest YoY Changes:")
            latest_yoy = yoy_changes.iloc[-1]
            for indicator, change in latest_yoy.items():
                if not pd.isna(change):
                    print(f"{indicator}: {change:+.2f}%")
        else:
            print("❌ No data available for DataFrame creation")
            
    except ImportError:
        print("⚠️ Pandas not installed. Install with: pip install pandas")
    except Exception as e:
        print(f"❌ Error in pandas integration: {e}")
    
    print()

def example_8_export_data():
    """Example 8: Export data to various formats"""
    print("=" * 60)
    print("💾 Example 8: Data Export Examples")
    print("=" * 60)
    
    # Load some economic data
    cpi_data = load_cached('cpi', '2024', standardized=True)
    
    if not cpi_data or not cpi_data['success']:
        print("❌ Failed to load data for export")
        return
    
    # Export to JSON
    try:
        with open('exported_cpi_data.json', 'w') as f:
            json.dump(cpi_data, f, indent=2, default=str)
        print("✅ Exported to exported_cpi_data.json")
    except Exception as e:
        print(f"❌ JSON export failed: {e}")
    
    # Export to CSV (simple format)
    try:
        import csv
        
        with open('exported_cpi_data.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Date', 'Value', 'Series_ID'])
            
                     data_points = cpi_data.get('data', [])
         series_info = cpi_data.get('series', {})
         for point in data_points:
             writer.writerow([point.get('date'), point.get('value'), series_info.get('id')])
        
        print("✅ Exported to exported_cpi_data.csv")
    except Exception as e:
        print(f"❌ CSV export failed: {e}")
    
    print()

def main():
    """Run all integration examples"""
    print("🚀 BLS Scraper API - Integration Examples")
    print("=" * 60)
    print()
    
    try:
        example_1_basic_usage()
        example_2_multi_indicator_analysis()
        example_3_inflation_tracker()
        example_4_fresh_vs_cached_comparison()
        example_5_standardized_format()
        example_6_error_handling()
        example_7_pandas_integration()
        example_8_export_data()
        
        print("=" * 60)
        print("✅ All integration examples completed successfully!")
        print("=" * 60)
        print()
        print("Next steps:")
        print("1. Copy any example code that fits your use case")
        print("2. Modify the examples for your specific requirements")
        print("3. Check the exported files (JSON/CSV) for data format")
        print("4. Review QUICK_START_GUIDE.md for more details")
        print("5. See API_REFERENCE.md for complete documentation")
        
    except KeyboardInterrupt:
        print("\n⚠️ Examples interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("Check that all dependencies are installed and you're in the project root")

if __name__ == "__main__":
    main() 