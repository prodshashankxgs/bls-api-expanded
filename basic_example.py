#!/usr/bin/env python3
"""
BLS Scraper API - Basic Example
A simple, unified example to test all core function behaviors
"""

import sys
from datetime import datetime, timedelta
from bls_snapshots import cpi, inflation, housing, services, complete

def test_basic_functionality():
    """Test basic functionality of all snapshot functions"""
    
    print("=" * 60)
    print("BLS SCRAPER API - BASIC FUNCTIONALITY TEST")
    print("=" * 60)
    
    # Test date (using recent date for better data availability)
    test_date = datetime.now() - timedelta(days=60)
    test_date_str = test_date.strftime('%Y-%m-%d')
    
    print(f"Testing with date: {test_date_str}")
    print("-" * 60)
    
    try:
        # Test 1: CPI Snapshot
        print("\n1. CPI SNAPSHOT TEST")
        print("-" * 30)
        cpi_data = cpi(test_date_str)
        print(f"✓ CPI data loaded successfully")
        print(f"  Shape: {cpi_data.shape}")
        print(f"  Columns: {list(cpi_data.columns)}")
        print(f"  Sample values:\n{cpi_data.head(3)}")
        
        # Test 2: Inflation Summary
        print("\n2. INFLATION SUMMARY TEST")
        print("-" * 35)
        inflation_data = inflation(test_date_str)
        print(f"✓ Inflation data loaded successfully")
        print(f"  Shape: {inflation_data.shape}")
        print(f"  Sample values:\n{inflation_data.head()}")
        
        # Test 3: Housing Data
        print("\n3. HOUSING DATA TEST")
        print("-" * 25)
        housing_data = housing(test_date_str)
        print(f"✓ Housing data loaded successfully")
        print(f"  Shape: {housing_data.shape}")
        print(f"  Sample values:\n{housing_data.head()}")
        
        # Test 4: Services Data
        print("\n4. SERVICES DATA TEST")
        print("-" * 26)
        services_data = services(test_date_str)
        print(f"✓ Services data loaded successfully")
        print(f"  Shape: {services_data.shape}")
        print(f"  Sample values:\n{services_data.head()}")
        
        # Test 5: Complete Snapshot
        print("\n5. COMPLETE SNAPSHOT TEST")
        print("-" * 30)
        complete_data = complete(test_date_str)
        print(f"✓ Complete snapshot loaded successfully")
        for key, data in complete_data.items():
            print(f"  {key}: {data.shape[0]} rows")
        
        # Test 6: Date Flexibility
        print("\n6. DATE FLEXIBILITY TEST")
        print("-" * 30)
        old_date = '2023-01-15'
        old_cpi = cpi(old_date)
        print(f"✓ Historical data works: {old_date}")
        print(f"  Shape: {old_cpi.shape}")

        # New Polars test
        print("\n7. POLARS INTEGRATION TEST")
        print("-" * 30)
        import polars as pl
        # Convert to Polars and reshape to long format
        polars_df = pl.from_pandas(cpi_data.reset_index())
        reshaped_df = polars_df.melt(
            id_vars=['Date', 'Adj'],
            variable_name='Item',
            value_name='Value'
        )
        # Reorder columns as requested: Item, Date, Value, Adj
        reshaped_df = reshaped_df.select(['Item', 'Date', 'Value', 'Adj'])
        print(f"✓ Polars DF created and reshaped successfully")
        print(f"  Original Shape: {polars_df.shape}")
        print(f"  Reshaped Shape: {reshaped_df.shape}")
        print(f"  Sample:\n{reshaped_df.head(5)}")
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED SUCCESSFULLY!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        print("=" * 60)
        return False

def show_usage_examples():
    """Show practical usage examples"""
    
    print("\n" + "=" * 60)
    print("USAGE EXAMPLES")
    print("=" * 60)
    
    print("""
# Get CPI data for a specific date
cpi_data = cpi('2024-01-15')

# Get inflation summary
inflation_data = inflation('2024-01-15')

# Get housing-specific data
housing_data = housing('2024-01-15')

# Get complete economic snapshot
all_data = complete(test_date_str)

# Access specific values
print(cpi_data.loc['CUSR0000SA0'])  # All items CPI
print(housing_data.loc['CUSR0000SAH'])  # Housing CPI

# Use in analysis
if all_data['cpi'] is not None:
    latest_cpi = all_data['cpi'].iloc[-1]
    print(f"Latest CPI: {latest_cpi}")
""")

def main():
    """Main execution function"""
    
    print("Starting BLS Scraper API basic functionality test...")
    
    success = test_basic_functionality()
    
    if success:
        show_usage_examples()
        print("\n🎉 Basic example completed successfully!")
        print("\nTo use in your own code:")
        print("from bls_snapshots import cpi, inflation, housing, services, complete")
    else:
        print("\n⚠️  Some tests failed. Check the error messages above.")
        sys.exit(1)

if __name__ == "__main__":
    main() 