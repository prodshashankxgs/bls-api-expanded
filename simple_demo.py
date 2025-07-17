#!/usr/bin/env python3
"""
Simple demo of the Fast BLS API
Just call load_data(ticker, date) to get CPI/PPI data quickly
"""

from app.fast_bls_api import load_data, FastBLSAPI

def main():
    print("🚀 Fast BLS API Demo - Simple Usage\n")
    
    # Create API instance
    api = FastBLSAPI()
    
    # Test 1: Simple CPI data
    print("📊 Loading CPI data for 2020-2023...")
    try:
        cpi_data = load_data('cpi', '2020-2023')
        print(f"✅ Success! Got {len(cpi_data)} CPI data points")
        if cpi_data:
            for point in cpi_data[:3]:  # Show first 3 points
                print(f"   {point['year']}: {point['value']}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Test 2: PPI data
    print("📊 Loading PPI data for 2022-2023...")
    try:
        ppi_data = load_data('ppi', '2022-2023')
        print(f"✅ Success! Got {len(ppi_data)} PPI data points")
        if ppi_data:
            for point in ppi_data:
                print(f"   {point['year']}: {point['value']}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Test 3: Check available data
    print("🔍 Available Data:")
    print("Available tickers:")
    for ticker, series_id in api.series_map.items():
        print(f"   {ticker} -> {series_id}")
    
    print("\nCached data series:")
    available = api.get_available_series()
    for series in available:
        print(f"   {series}")
    
    print("\n" + "="*50 + "\n")
    
    # Test 4: Try to get latest values
    print("Atempting to get latest values:")
    for ticker in ['cpi', 'ppi']:
        try:
            latest_list = api.get_latest(ticker)
            if latest_list:
                latest = latest_list[0]  # get_latest returns a list
                print(f"   {ticker.upper()}: {latest['value']} ({latest['date']})")
            else:
                print(f"   {ticker.upper()}: No data found")
        except Exception as e:
            print(f"   {ticker.upper()}: Error - {e}")

if __name__ == "__main__":
    main() 