#!/usr/bin/env python3
"""
Live BLS Data Scraping + Polars/Pandas Processing Example

This demonstrates exactly what you asked for:
- load_data(ticker, date) scrapes the BLS website live
- Process the data with Polars or Pandas
"""

from app.live_bls_scraper import load_data
import time

def main():
    print("🚀 Live BLS Data Scraping + Processing Demo")
    print("="*50)
    
    # STEP 1: Live scrape CPI data from BLS website
    print("\n📊 STEP 1: Live scraping CPI data...")
    start_time = time.time()
    
    cpi_data = load_data('cpi', '2022-2024')
    
    scrape_time = time.time() - start_time
    print(f"✅ Scraped {len(cpi_data)} CPI data points in {scrape_time:.2f} seconds")
    print(f"🌐 Data source: {cpi_data[0]['source'] if cpi_data else 'none'}")
    print(f"🕒 Scraped at: {cpi_data[0]['scraped_at'][:19] if cpi_data else 'none'}")
    
    if not cpi_data:
        print("❌ No data scraped - exiting")
        return
    
    # STEP 2: Process with Polars (if available)
    print("\n📈 STEP 2: Processing with Polars...")
    try:
        import polars as pl
        
        # Convert to Polars DataFrame
        df_polars = pl.DataFrame(cpi_data)
        
        print(f"✅ Created Polars DataFrame: {df_polars.shape}")
        print("\n📋 Data preview:")
        print(df_polars.select(['date', 'value', 'year']).head())
        
        # Polars analysis
        print("\n📊 Polars Analysis:")
        print(f"   Average CPI: {df_polars['value'].mean():.2f}")
        print(f"   Min CPI: {df_polars['value'].min():.2f}")
        print(f"   Max CPI: {df_polars['value'].max():.2f}")
        print(f"   Latest CPI: {df_polars['value'].first():.2f}")
        
        # Calculate month-over-month change with Polars
        df_with_change = df_polars.with_columns([
            ((pl.col('value') - pl.col('value').shift(1)) / pl.col('value').shift(1) * 100).alias('mom_change_pct')
        ])
        
        latest_change = df_with_change['mom_change_pct'].first()
        if latest_change is not None:
            print(f"   Latest month-over-month change: {latest_change:.2f}%")
        
    except ImportError:
        print("⚠️ Polars not installed - install with: pip install polars")
    
    # STEP 3: Process with Pandas
    print("\n🐼 STEP 3: Processing with Pandas...")
    try:
        import pandas as pd
        
        # Convert to Pandas DataFrame
        df_pandas = pd.DataFrame(cpi_data)
        
        print(f"✅ Created Pandas DataFrame: {df_pandas.shape}")
        print("\n📋 Data preview:")
        print(df_pandas[['date', 'value', 'year']].head())
        
        # Pandas analysis
        print("\n📊 Pandas Analysis:")
        print(f"   Average CPI: {df_pandas['value'].mean():.2f}")
        print(f"   Standard deviation: {df_pandas['value'].std():.2f}")
        print(f"   Data range: {df_pandas['date'].min()} to {df_pandas['date'].max()}")
        
        # Calculate rolling average
        df_pandas['rolling_avg'] = df_pandas['value'].rolling(window=3).mean()
        print(f"   Latest 3-month avg: {df_pandas['rolling_avg'].iloc[0]:.2f}")
        
    except ImportError:
        print("⚠️ Pandas not installed - install with: pip install pandas")
    
    # STEP 4: Live scrape PPI and compare
    print("\n💰 STEP 4: Live scraping PPI for comparison...")
    
    ppi_data = load_data('ppi', '2023-2024')
    
    if ppi_data:
        print(f"✅ Scraped {len(ppi_data)} PPI data points")
        
        try:
            import polars as pl
            
            # Compare CPI vs PPI with Polars
            cpi_recent = pl.DataFrame(cpi_data).filter(pl.col('year') >= 2023)
            ppi_recent = pl.DataFrame(ppi_data)
            
            print(f"\n📊 Recent Comparison (2023-2024):")
            print(f"   Latest CPI: {cpi_recent['value'].first():.2f}")
            print(f"   Latest PPI: {ppi_recent['value'].first():.2f}")
            print(f"   CPI-PPI Spread: {cpi_recent['value'].first() - ppi_recent['value'].first():.2f}")
            
        except ImportError:
            pass
    
    print(f"\n🎯 SUMMARY:")
    print(f"✅ Live scraped BLS data from website (NO cache, NO API)")
    print(f"✅ Processed with Polars/Pandas")
    print(f"✅ Total execution time: {time.time() - start_time:.2f} seconds")
    print(f"✅ Ready for your analysis!")

def simple_example():
    """Simple one-liner example"""
    print("\n🎯 SIMPLE EXAMPLE:")
    print("="*30)
    
    # This is exactly what you asked for:
    print("Code: cpi_data = load_data('cpi', '2022-2024')")
    
    cpi_data = load_data('cpi', '2022-2024')
    
    print(f"Result: {len(cpi_data)} data points scraped live from BLS")
    if cpi_data:
        print(f"Latest: {cpi_data[0]['value']} on {cpi_data[0]['date']}")
        print(f"Source: {cpi_data[0]['source']}")

if __name__ == "__main__":
    main()
    simple_example()
    
    print(f"\n✨ THAT'S IT! load_data(ticker, date) scrapes BLS website live!")
    print(f"🚀 Data is ready for Polars/Pandas processing!") 