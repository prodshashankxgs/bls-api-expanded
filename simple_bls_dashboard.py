#!/usr/bin/env python3
"""
Simple BLS API Dashboard with Polars Analytics

A clean demonstration of the BLS API capabilities:
- Performance comparison across all API methods
- Polars data analysis and statistics
- Simple but effective visualizations
- Professional metrics display

Perfect for showcasing to hedge funds!
"""

import polars as pl
import time
from datetime import datetime
import json

# Import all BLS API methods
from app.ultra_fresh_scraper import get_freshest_data
from app.live_bls_scraper import load_data as load_live
from app.fast_bls_api import load_data as load_cached

def test_all_apis(ticker: str = 'cpi', date_range: str = '2020-2025'):
    """Test all API methods and return performance metrics"""
    
    print(f"🚀 BLS API PERFORMANCE TEST")
    print("=" * 50)
    print(f"Ticker: {ticker.upper()} | Date Range: {date_range}")
    print()
    
    results = {}
    
    # Test 1: Ultra-Fresh API
    print("1️⃣ Ultra-Fresh API:")
    try:
        start_time = time.time()
        ultra_response = get_freshest_data(ticker, months_back=60, standardized=True)
        end_time = time.time()
        
        if ultra_response.get('success'):
            results['Ultra-Fresh'] = {
                'success': True,
                'data_points': ultra_response['metadata']['total_points'],
                'latency_ms': ultra_response['metadata']['latency_ms'],
                'quality': ultra_response['metadata']['quality'],
                'source': ultra_response['metadata']['source'],
                'actual_time': (end_time - start_time) * 1000,
                'response': ultra_response
            }
            print(f"   ✅ Success: {ultra_response['metadata']['total_points']} points in {ultra_response['metadata']['latency_ms']}ms")
        else:
            print(f"   ❌ Failed: {ultra_response.get('error', 'Unknown error')}")
            results['Ultra-Fresh'] = {'success': False, 'error': ultra_response.get('error')}
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        results['Ultra-Fresh'] = {'success': False, 'error': str(e)}
    
    # Test 2: Live Scraper API
    print("\n2️⃣ Live Scraper API:")
    try:
        start_time = time.time()
        live_response = load_live(ticker, date_range, standardized=True)
        end_time = time.time()
        
        if live_response.get('success'):
            results['Live Scraper'] = {
                'success': True,
                'data_points': live_response['metadata']['total_points'],
                'latency_ms': live_response['metadata']['latency_ms'],
                'quality': live_response['metadata']['quality'],
                'source': live_response['metadata']['source'],
                'actual_time': (end_time - start_time) * 1000,
                'response': live_response
            }
            print(f"   ✅ Success: {live_response['metadata']['total_points']} points in {live_response['metadata']['latency_ms']}ms")
        else:
            print(f"   ❌ Failed: {live_response.get('error', 'Unknown error')}")
            results['Live Scraper'] = {'success': False, 'error': live_response.get('error')}
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        results['Live Scraper'] = {'success': False, 'error': str(e)}
    
    # Test 3: Cached API
    print("\n3️⃣ Cached API:")
    try:
        start_time = time.time()
        cached_response = load_cached(ticker, date_range, standardized=True)
        end_time = time.time()
        
        if cached_response.get('success'):
            results['Cached'] = {
                'success': True,
                'data_points': cached_response['metadata']['total_points'],
                'latency_ms': cached_response['metadata']['latency_ms'],
                'quality': cached_response['metadata']['quality'],
                'source': cached_response['metadata']['source'],
                'actual_time': (end_time - start_time) * 1000,
                'response': cached_response
            }
            print(f"   ✅ Success: {cached_response['metadata']['total_points']} points in {cached_response['metadata']['latency_ms']}ms")
        else:
            print(f"   ❌ Failed: {cached_response.get('error', 'Unknown error')}")
            results['Cached'] = {'success': False, 'error': cached_response.get('error')}
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        results['Cached'] = {'success': False, 'error': str(e)}
    
    return results

def analyze_with_polars(api_response):
    """Analyze data using Polars"""
    
    if not (isinstance(api_response, dict) and api_response.get('success')):
        return None
    
    # Convert to Polars DataFrame
    data_points = api_response['data']
    df = pl.DataFrame(data_points)
    
    # Ensure proper data types
    df = df.with_columns([
        pl.col('date').str.to_date('%Y-%m-%d'),
        pl.col('value').cast(pl.Float64),
        pl.col('year').cast(pl.Int32),
        pl.col('month').cast(pl.Int32, strict=False)
    ])
    
    # Add calculated columns
    df = df.with_columns([
        pl.col('value').pct_change().alias('monthly_change_pct'),
        (pl.col('value') / pl.col('value').shift(12) - 1).alias('yearly_change_pct')
    ])
    
    return df

def display_performance_metrics(results):
    """Display performance comparison table"""
    
    print("\n📊 PERFORMANCE COMPARISON")
    print("=" * 60)
    print(f"{'API Method':<15} {'Success':<8} {'Points':<8} {'Latency':<10} {'Quality':<8}")
    print("-" * 60)
    
    for api_name, result in results.items():
        if result.get('success'):
            print(f"{api_name:<15} {'✅':<8} {result['data_points']:<8} {result['latency_ms']:<7}ms {result['quality']:<8}")
        else:
            print(f"{api_name:<15} {'❌':<8} {'0':<8} {'N/A':<10} {'failed':<8}")

def display_polars_analysis(df, series_info):
    """Display comprehensive Polars data analysis"""
    
    if df is None or df.is_empty():
        print("\n⚠️  No data available for analysis")
        return
    
    print("\n📈 POLARS DATA ANALYSIS")
    print("=" * 50)
    
    # Basic info
    print(f"📊 Data Shape: {df.shape[0]} rows × {df.shape[1]} columns")
    print(f"📅 Date Range: {df['date'].min()} to {df['date'].max()}")
    print(f"📋 Series: {series_info['name']}")
    print(f"🏢 Source: {series_info['source_agency']}")
    print(f"📏 Units: {series_info['units']}")
    
    # Statistical summary
    stats = df.select([
        pl.col('value').mean().alias('mean'),
        pl.col('value').median().alias('median'),
        pl.col('value').std().alias('std_dev'),
        pl.col('value').min().alias('min'),
        pl.col('value').max().alias('max'),
        pl.col('value').quantile(0.25).alias('q1'),
        pl.col('value').quantile(0.75).alias('q3')
    ]).to_dicts()[0]
    
    print(f"\n📈 STATISTICAL SUMMARY:")
    print(f"   Mean:     {stats['mean']:.3f}")
    print(f"   Median:   {stats['median']:.3f}")
    print(f"   Std Dev:  {stats['std_dev']:.3f}")
    print(f"   Min:      {stats['min']:.3f}")
    print(f"   Max:      {stats['max']:.3f}")
    print(f"   Q1:       {stats['q1']:.3f}")
    print(f"   Q3:       {stats['q3']:.3f}")
    
    # Recent trend analysis
    if len(df) >= 2:
        latest_value = df['value'][0]
        previous_value = df['value'][1]
        change = ((latest_value - previous_value) / previous_value) * 100
        print(f"\n📊 LATEST TREND:")
        print(f"   Current Value: {latest_value:.3f}")
        print(f"   Previous Value: {previous_value:.3f}")
        print(f"   Monthly Change: {change:+.2f}%")
    
    # Year-over-year analysis
    yoy_data = df.filter(pl.col('yearly_change_pct').is_not_null())
    if not yoy_data.is_empty():
        latest_yoy = yoy_data['yearly_change_pct'][0] * 100
        avg_yoy = yoy_data['yearly_change_pct'].mean() * 100
        print(f"\n📅 YEAR-OVER-YEAR ANALYSIS:")
        print(f"   Latest YoY: {latest_yoy:+.2f}%")
        print(f"   Average YoY: {avg_yoy:+.2f}%")
    
    # Recent data points
    print(f"\n📋 RECENT DATA (Last 5 points):")
    recent_data = df.head(5).select(['date', 'value', 'monthly_change_pct'])
    for row in recent_data.to_dicts():
        monthly_change = row['monthly_change_pct']
        change_str = f"{monthly_change*100:+.2f}%" if monthly_change is not None else "N/A"
        print(f"   {row['date']}: {row['value']:.3f} ({change_str})")

def create_simple_charts(df, series_info):
    """Create simple ASCII charts"""
    
    if df is None or df.is_empty():
        return
    
    print("\n📊 SIMPLE DATA VISUALIZATION")
    print("=" * 50)
    
    # Get recent 12 months of data
    recent_df = df.head(12)
    values = recent_df['value'].to_list()
    dates = recent_df['date'].to_list()
    
    print("📈 Recent 12-Month Trend (ASCII Chart):")
    print("-" * 40)
    
    # Normalize values for ASCII chart (scale 0-20)
    min_val = min(values)
    max_val = max(values)
    value_range = max_val - min_val
    
    for i, (date, value) in enumerate(zip(dates, values)):
        # Scale to 0-20 range
        if value_range > 0:
            scaled = int(((value - min_val) / value_range) * 20)
        else:
            scaled = 10
        
        bar = "█" * scaled + "░" * (20 - scaled)
        print(f"{str(date)[:7]}: {bar} {value:.1f}")
    
    print(f"\nScale: {min_val:.1f} {'░' * 20} {max_val:.1f}")

def run_dashboard(ticker: str = 'cpi', date_range: str = '2020-2025'):
    """Main dashboard function"""
    
    print("🏢 BLS API PROFESSIONAL DASHBOARD")
    print("=" * 60)
    print(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test all APIs
    results = test_all_apis(ticker, date_range)
    
    # Display performance metrics
    display_performance_metrics(results)
    
    # Find the best successful response
    best_response = None
    best_api = None
    
    for api_name, result in results.items():
        if result.get('success'):
            best_response = result['response']
            best_api = api_name
            break
    
    if best_response:
        print(f"\n🎯 Using {best_api} data for analysis...")
        
        # Polars analysis
        df = analyze_with_polars(best_response)
        display_polars_analysis(df, best_response['series'])
        
        # Simple charts
        create_simple_charts(df, best_response['series'])
        
        # Export data option
        if df is not None and not df.is_empty():
            print(f"\n💾 DATA EXPORT OPTIONS:")
            print(f"   • df.write_csv('bls_data_{ticker}_{datetime.now().strftime('%Y%m%d')}.csv')")
            print(f"   • df.write_json('bls_data_{ticker}_{datetime.now().strftime('%Y%m%d')}.json')")
            print(f"   • df.write_parquet('bls_data_{ticker}_{datetime.now().strftime('%Y%m%d')}.parquet')")
    
    else:
        print("\n❌ No successful API responses available for analysis")
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 DASHBOARD SUMMARY")
    print("=" * 60)
    
    successful_apis = [name for name, result in results.items() if result.get('success')]
    print(f"✅ Successful APIs: {len(successful_apis)}/3 ({', '.join(successful_apis)})")
    
    if successful_apis:
        # Performance comparison
        fastest_time = min([results[api]['latency_ms'] for api in successful_apis])
        fastest_api = [api for api in successful_apis if results[api]['latency_ms'] == fastest_time][0]
        
        most_data = max([results[api]['data_points'] for api in successful_apis])
        most_data_api = [api for api in successful_apis if results[api]['data_points'] == most_data][0]
        
        print(f"🚀 Fastest Response: {fastest_api} ({fastest_time}ms)")
        print(f"📊 Most Data Points: {most_data_api} ({most_data} points)")
        
        if best_response:
            latest_point = best_response['data'][0]
            print(f"📈 Latest {ticker.upper()}: {latest_point['value']} ({latest_point['date']})")
    
    print(f"\n🕐 Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🎯 BLS API Dashboard - Ready for Production Trading Systems!")

if __name__ == "__main__":
    # Customize these parameters
    TICKER = 'cpi'  # Options: 'cpi', 'ppi', 'unemployment', 'cpi_core'
    DATE_RANGE = '2020-2025'
    
    # Check dependencies
    try:
        import polars as pl
        print("✅ Polars available")
    except ImportError:
        print("❌ Please install: pip install polars")
        exit(1)
    
    # Run the dashboard
    run_dashboard(TICKER, DATE_RANGE) 