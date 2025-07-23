#!/usr/bin/env python3
"""
Comprehensive CPI & PPI Data Example
===================================

This script demonstrates loading and displaying all available CPI and PPI data
using the optimized load_data system. Shows both individual tickers and
comprehensive economic indicators.

Usage:
    python3 comprehensive_example.py
"""

from data_loader import DataLoader, load_data, BLSDataClient, get_all_tickers
import polars as pl
import time

def load_all_cpi_ppi_data():
    """Load comprehensive CPI and PPI data and display formatted results"""
    
    print("🏛️  COMPREHENSIVE BLS CPI & PPI DATA LOADER")
    print("=" * 70)
    print("Loading all available economic indicators...")
    print()
    
    # Initialize the data loader
    dl = DataLoader()
    client = BLSDataClient()
    
    # System status check
    health_status = dl.health_check()
    print(f"📊 System Status: {'✅ Ready' if health_status else '⚠️  Limited (will use available data)'}")
    
    # Get Excel file info
    excel_info = dl.get_excel_info()
    print(f"📁 Excel Files: {len(excel_info['available_files'])} available")
    
    print(f"🔄 Cache Status: Enabled with performance optimization")
    print()
    
    # Define comprehensive CPI and PPI tickers
    core_indicators = [
        # Core CPI Indicators
        "CPSCJEWE Index",      # All items CPI (Headline)
        "CPIQWAN Index",       # Core CPI (Less Food/Energy)
        
        # Food & Energy
        "Food",                # Food CPI
        "Food at home",        # Food at home
        "Energy",              # Energy CPI
        
        # Housing
        "Shelter",             # Housing costs
        "Owners' equivalent rent of residences",  # Rent equivalent
        
        # Clothing (Your specific interest)
        "CPSCWG Index",        # Women's clothing
        "CPSCMB Index",        # Men's clothing  
        "CPSCINTD Index",      # Children's clothing
        "CPIQSMFN Index",      # Clothing materials
        "CPSCJEWE Index (Jewelry)",  # Jewelry
        
        # Services
        "Services less energy services",  # Core services
        "Medical care services",          # Healthcare
        "Transportation services",        # Transportation
        "Motor vehicle insurance",        # Auto insurance
        "Airline fares",                  # Air travel
        
        # Commodities
        "Commodities less food and energy commodities"  # Core goods
    ]
    
    print("📈 LOADING CORE CPI INDICATORS")
    print("-" * 50)
    
    # Load all core indicators
    start_time = time.time()
    df_core = dl.load_data(core_indicators, "latest")
    load_time = time.time() - start_time
    
    print(f"✅ Loaded {df_core.shape[0]} data points in {load_time:.3f} seconds")
    print(f"📊 Categories covered: {df_core.select('category').unique().shape[0]} unique categories")
    print()
    
    # Display core CPI data
    if not df_core.is_empty():
        print("🎯 HEADLINE & CORE CPI DATA")
        print("-" * 40)
        
        # Filter and display headline indicators
        headline_data = df_core.filter(
            pl.col('ticker').is_in(['CPSCJEWE Index', 'CPIQWAN Index', 'Food', 'Energy'])
        ).select([
            'ticker',
            'expenditure_category', 
            'relative_importance_pct',
            'unadj_pct_change_12mo',
            'unadj_pct_change_1mo',
            'category'
        ])
        
        print(headline_data)
        print()
        
        # Show clothing breakdown (your specific interest)
        print("👕 CLOTHING & APPAREL BREAKDOWN")
        print("-" * 40)
        
        clothing_data = df_core.filter(
            pl.col('category').str.contains('clothing|jewelry')
        ).select([
            'ticker',
            'expenditure_category',
            'relative_importance_pct', 
            'unadj_pct_change_12mo',
            'category'
        ])
        
        if not clothing_data.is_empty():
            print(clothing_data)
        else:
            print("No clothing data available in current dataset")
        print()
        
        # Show services vs goods breakdown
        print("🏪 SERVICES VS GOODS ANALYSIS")
        print("-" * 40)
        
        services_goods = df_core.filter(
            pl.col('category').is_in(['services', 'goods'])
        ).select([
            'expenditure_category',
            'relative_importance_pct',
            'unadj_pct_change_12mo', 
            'category'
        ])
        
        if not services_goods.is_empty():
            print(services_goods)
        else:
            # Show alternative breakdown
            alternative_breakdown = df_core.select([
                'expenditure_category',
                'relative_importance_pct',
                'unadj_pct_change_12mo',
                'category'
            ]).head(8)
            print("Alternative economic categories:")
            print(alternative_breakdown)
        print()
    
    # Load additional economic indicators (simulated PPI and others)
    print("📊 ADDITIONAL ECONOMIC INDICATORS")
    print("-" * 50)
    
    # Try to get PPI-related or additional data
    additional_indicators = []
    all_available = get_all_tickers()
    
    # Look for PPI-like indicators or additional categories
    for ticker in all_available:
        if ticker not in core_indicators:
            additional_indicators.append(ticker)
    
    if additional_indicators:
        print(f"Found {len(additional_indicators)} additional indicators")
        
        # Load a sample of additional indicators
        sample_additional = additional_indicators[:5]  # Take first 5
        df_additional = dl.load_data(sample_additional, "latest")
        
        if not df_additional.is_empty():
            print("Sample additional economic data:")
            additional_sample = df_additional.select([
                'ticker',
                'expenditure_category',
                'relative_importance_pct',
                'category'
            ]).head(5)
            print(additional_sample)
        print()
    
    # Comprehensive dataset summary
    print("📋 COMPREHENSIVE DATASET SUMMARY")
    print("-" * 50)
    
    # Get complete dataset using client
    try:
        complete_data = client.get_complete_dataset()
        if not complete_data.is_empty():
            print(f"📊 Complete Dataset: {complete_data.shape[0]} total data points")
            print(f"🏷️  Unique Categories: {complete_data.select('category').unique().shape[0]}")
            print(f"🎯 Unique Tickers: {complete_data.select('ticker').unique().shape[0]}")
            
            # Show category breakdown
            category_counts = complete_data.group_by('category').agg([
                pl.count().alias('count'),
                pl.col('relative_importance_pct').cast(pl.Utf8).str.replace(',', '').cast(pl.Float64, strict=False).mean().alias('avg_weight')
            ]).sort('count', descending=True)
            
            print("\n📈 Categories by data point count:")
            print(category_counts.head(8))
            
        else:
            print("Complete dataset not available, using loaded data")
            
    except Exception as e:
        print(f"Note: Complete dataset access limited: {e}")
    
    # Performance and data source summary
    print("\n⚡ PERFORMANCE & DATA SOURCES")
    print("-" * 50)
    
    # Show cache performance if available
    cache_stats = getattr(client, '_get_cache_stats', lambda: {})()
    if cache_stats:
        print(f"🚀 Cache Performance:")
        print(f"   • Hit Rate: {cache_stats.get('hit_rate', 0):.1%}")
        print(f"   • Total Requests: {cache_stats.get('requests', 0)}")
        print(f"   • Cache Size: {cache_stats.get('size', 0)} items")
    
    # Data source breakdown
    if not df_core.is_empty() and 'ticker' in df_core.columns:
        total_points = df_core.shape[0]
        print(f"📊 Data Points Loaded: {total_points}")
        print(f"⏱️  Load Time: {load_time:.3f} seconds")
        print(f"🎯 Success Rate: {(total_points / len(core_indicators) * 100):.1f}%")
    
    print("\n💾 SAVE OPTIONS")
    print("-" * 20)
    
    # Save the comprehensive data
    output_file = "comprehensive_cpi_ppi_data.csv"
    dl.save_data(df_core, output_file)
    print(f"✅ Data saved to: {output_file}")
    
    # Save summary to JSON for easy analysis
    summary_data = {
        "load_time": load_time,
        "total_indicators": len(core_indicators),
        "data_points": df_core.shape[0] if not df_core.is_empty() else 0,
        "categories": df_core.select('category').unique().shape[0] if not df_core.is_empty() else 0,
        "system_health": health_status,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    import json
    with open("data_summary.json", "w") as f:
        json.dump(summary_data, f, indent=2)
    print(f"📊 Summary saved to: data_summary.json")
    
    print("\n🎉 DATA LOADING COMPLETE!")
    print("=" * 70)
    print("Use the loaded data for your economic analysis.")
    print(f"Next steps: Open {output_file} in Excel or continue with Python analysis")
    
    return df_core

def show_usage_examples():
    """Show practical usage examples for the loaded data"""
    print("\n\n🛠️  PRACTICAL USAGE EXAMPLES")
    print("=" * 50)
    
    print("Example 1: Quick CPI check")
    print("```python")
    print("from data_loader import load_data")
    print("cpi_data = load_data('CPSCJEWE Index', 'latest')")
    print("print(f'Current CPI: {cpi_data[\"unadj_index_jun2025\"][0]}')")
    print("```")
    print()
    
    print("Example 2: Your exact pattern")
    print("```python") 
    print("from data_loader import DataLoader")
    print("tickers = ['CPSCJEWE Index', 'CPIQWAN Index', 'CPSCWG Index']")
    print("dl = DataLoader()")
    print("df = dl.load_data(tickers, '2025-01-01')")
    print("```")
    print()
    
    print("Example 3: Advanced analysis")
    print("```python")
    print("from data_loader import BLSDataClient")
    print("client = BLSDataClient()")
    print("clothing_data = client.search_categories('clothing')")
    print("weights = client.get_weights()")
    print("```")

if __name__ == "__main__":
    try:
        # Run the comprehensive data loading
        df = load_all_cpi_ppi_data()
        
        # Show usage examples
        show_usage_examples()
        
        print(f"\n✅ Script completed successfully!")
        print(f"📊 Loaded data shape: {df.shape if df is not None and not df.is_empty() else 'No data'}")
        
    except Exception as e:
        print(f"❌ Error running comprehensive example: {e}")
        print("This might be due to missing dependencies or data files.")
        print("Try running: python3 auto_scraper.py first to ensure data is available.") 