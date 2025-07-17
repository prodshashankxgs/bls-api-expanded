#!/usr/bin/env python3
"""
BLS API Data Dashboard with Polars Analytics

This script demonstrates the professional capabilities of the BLS API by:
- Fetching economic data using multiple API methods
- Analyzing data with Polars (high-performance DataFrames)
- Creating visualizations and charts
- Displaying comprehensive performance metrics
- Showing professional data quality indicators

Perfect for demonstrating to hedge funds and trading firms.
"""

import polars as pl
import matplotlib.pyplot as plt
import seaborn as sns
import time
from datetime import datetime, timedelta
import json
from typing import Dict, List, Any
import numpy as np

# Import all BLS API methods
from app.ultra_fresh_scraper import get_freshest_data
from app.live_bls_scraper import load_data as load_live
from app.fast_bls_api import load_data as load_cached

def create_performance_metrics(api_responses: Dict[str, Any]) -> pl.DataFrame:
    """Create performance metrics comparison DataFrame"""
    
    metrics_data = []
    for api_name, response in api_responses.items():
        if isinstance(response, dict) and response.get('success'):
            metadata = response['metadata']
            metrics_data.append({
                'api_method': api_name,
                'latency_ms': metadata['latency_ms'],
                'data_points': metadata['total_points'],
                'data_quality': metadata['quality'],
                'source': metadata['source'],
                'api_version': metadata['api_version'],
                'timestamp': metadata['timestamp']
            })
        else:
            metrics_data.append({
                'api_method': api_name,
                'latency_ms': 0,
                'data_points': 0,
                'data_quality': 'failed',
                'source': 'error',
                'api_version': 'N/A',
                'timestamp': datetime.now().isoformat()
            })
    
    return pl.DataFrame(metrics_data)

def convert_to_polars(api_response: Dict[str, Any]) -> pl.DataFrame:
    """Convert API response to Polars DataFrame"""
    
    if not (isinstance(api_response, dict) and api_response.get('success')):
        return pl.DataFrame()
    
    # Extract data points
    data_points = api_response['data']
    
    # Convert to Polars DataFrame
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
        pl.col('date').dt.strftime('%Y-%m').alias('period_str'),
        pl.col('value').pct_change().alias('monthly_change_pct'),
        (pl.col('value') / pl.col('value').shift(12) - 1).alias('yearly_change_pct')
    ])
    
    return df

def create_visualizations(df: pl.DataFrame, series_info: Dict[str, Any], save_plots: bool = True):
    """Create comprehensive data visualizations"""
    
    if df.is_empty():
        print("⚠️  No data available for visualization")
        return
    
    # Set up the plotting style
    plt.style.use('seaborn-v0_8')
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle(f'{series_info["name"]} - Professional Data Analysis', fontsize=16, fontweight='bold')
    
    # Convert to pandas for plotting (Polars plotting support is limited)
    pdf = df.to_pandas()
    
    # 1. Time Series Plot
    axes[0, 0].plot(pdf['date'], pdf['value'], linewidth=2, color='#2E86AB', marker='o', markersize=4)
    axes[0, 0].set_title('Time Series Trend', fontweight='bold')
    axes[0, 0].set_xlabel('Date')
    axes[0, 0].set_ylabel(f'Value ({series_info["units"]})')
    axes[0, 0].grid(True, alpha=0.3)
    axes[0, 0].tick_params(axis='x', rotation=45)
    
    # 2. Monthly Change Distribution
    monthly_changes = pdf['monthly_change_pct'].dropna()
    if len(monthly_changes) > 0:
        axes[0, 1].hist(monthly_changes, bins=15, alpha=0.7, color='#A23B72', edgecolor='black')
        axes[0, 1].axvline(monthly_changes.mean(), color='red', linestyle='--', linewidth=2, label=f'Mean: {monthly_changes.mean():.3f}%')
        axes[0, 1].set_title('Monthly Change Distribution', fontweight='bold')
        axes[0, 1].set_xlabel('Monthly Change (%)')
        axes[0, 1].set_ylabel('Frequency')
        axes[0, 1].legend()
        axes[0, 1].grid(True, alpha=0.3)
    
    # 3. Year-over-Year Changes
    yearly_data = pdf[pdf['yearly_change_pct'].notna()]
    if len(yearly_data) > 0:
        bars = axes[1, 0].bar(yearly_data['date'], yearly_data['yearly_change_pct'] * 100, 
                             color=['#F18F01' if x >= 0 else '#C73E1D' for x in yearly_data['yearly_change_pct']])
        axes[1, 0].set_title('Year-over-Year Changes', fontweight='bold')
        axes[1, 0].set_xlabel('Date')
        axes[1, 0].set_ylabel('YoY Change (%)')
        axes[1, 0].grid(True, alpha=0.3)
        axes[1, 0].tick_params(axis='x', rotation=45)
        axes[1, 0].axhline(y=0, color='black', linestyle='-', alpha=0.8)
    
    # 4. Recent Trend (Last 12 months)
    recent_data = pdf.tail(12)
    axes[1, 1].plot(recent_data['date'], recent_data['value'], linewidth=3, color='#2E86AB', marker='o', markersize=6)
    axes[1, 1].fill_between(recent_data['date'], recent_data['value'], alpha=0.3, color='#2E86AB')
    axes[1, 1].set_title('Recent Trend (Last 12 Months)', fontweight='bold')
    axes[1, 1].set_xlabel('Date')
    axes[1, 1].set_ylabel(f'Value ({series_info["units"]})')
    axes[1, 1].grid(True, alpha=0.3)
    axes[1, 1].tick_params(axis='x', rotation=45)
    
    # Add data source annotation
    fig.text(0.02, 0.02, f'Data Source: {series_info["source_agency"]} | Frequency: {series_info["frequency"]} | Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}', 
             fontsize=8, alpha=0.7)
    
    plt.tight_layout()
    
    if save_plots:
        filename = f'bls_analysis_{series_info["id"]}_{datetime.now().strftime("%Y%m%d_%H%M")}.png'
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"📊 Charts saved as: {filename}")
    
    plt.show()

def create_performance_dashboard(performance_df: pl.DataFrame):
    """Create performance comparison dashboard"""
    
    if performance_df.is_empty():
        print("⚠️  No performance data available")
        return
    
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    fig.suptitle('BLS API Performance Dashboard', fontsize=16, fontweight='bold')
    
    pdf = performance_df.to_pandas()
    
    # 1. Latency Comparison
    axes[0].bar(pdf['api_method'], pdf['latency_ms'], color=['#2E86AB', '#A23B72', '#F18F01'])
    axes[0].set_title('API Response Times', fontweight='bold')
    axes[0].set_xlabel('API Method')
    axes[0].set_ylabel('Latency (ms)')
    axes[0].tick_params(axis='x', rotation=45)
    
    # Add value labels on bars
    for i, v in enumerate(pdf['latency_ms']):
        axes[0].text(i, v + max(pdf['latency_ms']) * 0.01, f'{int(v)}ms', ha='center', fontweight='bold')
    
    # 2. Data Points Retrieved
    axes[1].bar(pdf['api_method'], pdf['data_points'], color=['#2E86AB', '#A23B72', '#F18F01'])
    axes[1].set_title('Data Points Retrieved', fontweight='bold')
    axes[1].set_xlabel('API Method')
    axes[1].set_ylabel('Number of Points')
    axes[1].tick_params(axis='x', rotation=45)
    
    # Add value labels
    for i, v in enumerate(pdf['data_points']):
        axes[1].text(i, v + max(pdf['data_points']) * 0.01, f'{int(v)}', ha='center', fontweight='bold')
    
    # 3. Data Quality Overview
    quality_colors = {'high': '#2E86AB', 'medium': '#F18F01', 'low': '#C73E1D', 'failed': '#808080'}
    colors = [quality_colors.get(q, '#808080') for q in pdf['data_quality']]
    axes[2].bar(pdf['api_method'], [1]*len(pdf), color=colors)
    axes[2].set_title('Data Quality Indicators', fontweight='bold')
    axes[2].set_xlabel('API Method')
    axes[2].set_ylabel('Quality Level')
    axes[2].set_yticks([0.2, 0.5, 0.8])
    axes[2].set_yticklabels(['Low', 'Medium', 'High'])
    axes[2].tick_params(axis='x', rotation=45)
    
    # Add quality labels
    for i, q in enumerate(pdf['data_quality']):
        axes[2].text(i, 0.5, q.upper(), ha='center', va='center', fontweight='bold', color='white')
    
    plt.tight_layout()
    
    filename = f'performance_dashboard_{datetime.now().strftime("%Y%m%d_%H%M")}.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"⚡ Performance dashboard saved as: {filename}")
    
    plt.show()

def run_bls_dashboard(ticker: str = 'cpi', date_range: str = '2022-2025'):
    """Main dashboard function"""
    
    print("🚀 BLS API DATA DASHBOARD")
    print("=" * 60)
    print(f"Ticker: {ticker.upper()} | Date Range: {date_range}")
    print()
    
    # Test all API methods
    print("📊 Testing all API methods...")
    
    api_responses = {}
    
    # 1. Ultra-Fresh API
    print("\n1️⃣ Ultra-Fresh API:")
    start_time = time.time()
    try:
        ultra_response = get_freshest_data(ticker, months_back=36, standardized=True)
        api_responses['Ultra-Fresh'] = ultra_response
        if ultra_response.get('success'):
            print(f"   ✅ Success: {ultra_response['metadata']['total_points']} points in {ultra_response['metadata']['latency_ms']}ms")
        else:
            print(f"   ❌ Failed: {ultra_response.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        api_responses['Ultra-Fresh'] = {'success': False, 'error': str(e)}
    
    # 2. Live Scraper API
    print("\n2️⃣ Live Scraper API:")
    try:
        live_response = load_live(ticker, date_range, standardized=True)
        api_responses['Live Scraper'] = live_response
        if live_response.get('success'):
            print(f"   ✅ Success: {live_response['metadata']['total_points']} points in {live_response['metadata']['latency_ms']}ms")
        else:
            print(f"   ❌ Failed: {live_response.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        api_responses['Live Scraper'] = {'success': False, 'error': str(e)}
    
    # 3. Cached API
    print("\n3️⃣ Cached API:")
    try:
        cached_response = load_cached(ticker, date_range, standardized=True)
        api_responses['Cached'] = cached_response
        if cached_response.get('success'):
            print(f"   ✅ Success: {cached_response['metadata']['total_points']} points in {cached_response['metadata']['latency_ms']}ms")
        else:
            print(f"   ❌ Failed: {cached_response.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        api_responses['Cached'] = {'success': False, 'error': str(e)}
    
    # Create performance metrics
    print("\n📈 Creating performance analysis...")
    performance_df = create_performance_metrics(api_responses)
    
    # Use the best available response for data analysis
    best_response = None
    for response in api_responses.values():
        if isinstance(response, dict) and response.get('success'):
            best_response = response
            break
    
    if best_response:
        print(f"\n🎯 Using {best_response['metadata']['source']} data for analysis...")
        
        # Convert to Polars DataFrame
        data_df = convert_to_polars(best_response)
        
        # Display Polars analysis
        print("\n📊 POLARS DATA ANALYSIS:")
        print("-" * 40)
        print(f"Data shape: {data_df.shape}")
        print(f"Date range: {data_df['date'].min()} to {data_df['date'].max()}")
        
        if not data_df.is_empty():
            # Basic statistics
            stats = data_df.select([
                pl.col('value').mean().alias('mean'),
                pl.col('value').median().alias('median'),
                pl.col('value').std().alias('std_dev'),
                pl.col('value').min().alias('min'),
                pl.col('value').max().alias('max')
            ]).to_dicts()[0]
            
            print(f"\n📈 Statistical Summary:")
            for stat, value in stats.items():
                print(f"   {stat.capitalize()}: {value:.3f}")
            
            # Recent trend
            if len(data_df) >= 2:
                latest_value = data_df['value'][0]
                previous_value = data_df['value'][1]
                change = ((latest_value - previous_value) / previous_value) * 100
                print(f"\n📊 Latest trend: {change:+.2f}% change")
            
            # Year-over-year if available
            yoy_data = data_df.filter(pl.col('yearly_change_pct').is_not_null())
            if not yoy_data.is_empty():
                latest_yoy = yoy_data['yearly_change_pct'][0] * 100
                print(f"📅 Year-over-year: {latest_yoy:+.2f}%")
        
        # Create visualizations
        print("\n🎨 Creating visualizations...")
        create_visualizations(data_df, best_response['series'])
        
    else:
        print("\n❌ No successful API responses available for analysis")
    
    # Create performance dashboard
    print("\n⚡ Creating performance dashboard...")
    create_performance_dashboard(performance_df)
    
    # Display summary
    print("\n" + "=" * 60)
    print("📋 DASHBOARD SUMMARY")
    print("=" * 60)
    
    # Performance summary
    if not performance_df.is_empty():
        fastest_api = performance_df.filter(pl.col('latency_ms') > 0).sort('latency_ms')[0, 'api_method']
        most_data = performance_df.sort('data_points', descending=True)[0, 'api_method']
        
        print(f"🚀 Fastest API: {fastest_api}")
        print(f"📊 Most data points: {most_data}")
        print(f"✅ Successful APIs: {len(performance_df.filter(pl.col('data_quality') != 'failed'))}/3")
    
    # Data summary
    if best_response:
        latest_point = best_response['data'][0]
        print(f"📈 Latest {ticker.upper()}: {latest_point['value']} ({latest_point['date']})")
        print(f"🎯 Data quality: {best_response['metadata']['quality']}")
        print(f"📡 Data source: {best_response['metadata']['source']}")
    
    print(f"\n🕐 Dashboard completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("📁 Check current directory for saved charts!")

if __name__ == "__main__":
    # You can customize these parameters
    TICKER = 'cpi'  # Options: 'cpi', 'ppi', 'unemployment', 'cpi_core'
    DATE_RANGE = '2020-2025'  # Adjust as needed
    
    # Install required packages if needed
    try:
        import polars as pl
        import matplotlib.pyplot as plt
        import seaborn as sns
    except ImportError as e:
        print("❌ Missing required packages!")
        print("Please install: pip install polars matplotlib seaborn")
        print(f"Error: {e}")
        exit(1)
    
    # Run the dashboard
    run_bls_dashboard(TICKER, DATE_RANGE) 