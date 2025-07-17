#!/usr/bin/env python3
"""
BLS Scraper API - Installation Test

Run this script to verify that the BLS API is properly installed and working.

Usage:
    python test_installation.py
"""

import sys
import time
from datetime import datetime

def test_imports():
    """Test that all required modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        from app.fast_bls_api import load_data as load_cached
        from app.fast_bls_api import FastBLSAPI
        print("✅ Fast BLS API imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import Fast BLS API: {e}")
        return False
    
    try:
        from app.live_bls_scraper import load_data as load_live
        from app.live_bls_scraper import LiveBLSScraper
        print("✅ Live BLS Scraper imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import Live BLS Scraper: {e}")
        return False
    
    try:
        from app.standardized_schema import StandardizedDataFormatter
        print("✅ Standardized Schema imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import Standardized Schema: {e}")
        return False
    
    return True

def test_cached_api():
    """Test the cached data API"""
    print("\n📊 Testing cached data API...")
    
    try:
        from app.fast_bls_api import load_data
        
        # Test basic functionality
        start_time = time.time()
        cpi_data = load_data('cpi', '2024')
        load_time = (time.time() - start_time) * 1000
        
        if cpi_data:
            print(f"✅ Loaded {len(cpi_data)} CPI data points in {load_time:.1f}ms")
            print(f"   Latest CPI: {cpi_data[0]['value']} ({cpi_data[0]['date']})")
            return True
        else:
            print("❌ No data returned from cached API")
            return False
            
    except Exception as e:
        print(f"❌ Cached API test failed: {e}")
        return False

def test_standardized_format():
    """Test the standardized data format"""
    print("\n🏛️ Testing standardized format...")
    
    try:
        from app.fast_bls_api import load_data
        
        response = load_data('cpi', '2024', standardized=True)
        
        if response and isinstance(response, dict) and response.get('success'):
            print("✅ Standardized format working")
            print(f"   API version: {response.get('metadata', {}).get('api_version')}")
            print(f"   Data quality: {response.get('metadata', {}).get('quality')}")
            print(f"   Series ID: {response.get('series', {}).get('id')}")
            return True
        else:
            print("❌ Standardized format test failed")
            return False
            
    except Exception as e:
        print(f"❌ Standardized format test failed: {e}")
        return False

def test_live_scraper():
    """Test the live scraper (optional - requires internet)"""
    print("\n🌐 Testing live scraper (this may take a few seconds)...")
    
    try:
        from app.live_bls_scraper import load_data
        
        print("   Attempting live scrape...")
        start_time = time.time()
        live_data = load_data('cpi', '2024')
        scrape_time = (time.time() - start_time) * 1000
        
        if live_data:
            print(f"✅ Live scraper working - {len(live_data)} points in {scrape_time:.0f}ms")
            print(f"   Fresh CPI: {live_data[0]['value']} ({live_data[0]['date']})")
            if 'scraped_at' in live_data[0]:
                print(f"   Scraped at: {live_data[0]['scraped_at']}")
            return True
        else:
            print("⚠️ Live scraper returned no data (may be normal)")
            return True  # Don't fail the test for this
            
    except Exception as e:
        print(f"⚠️ Live scraper test failed: {e}")
        print("   This is normal if you don't have internet or sites are down")
        return True  # Don't fail the test for this

def test_multi_indicator():
    """Test loading multiple indicators"""
    print("\n🔄 Testing multi-indicator loading...")
    
    try:
        from app.fast_bls_api import FastBLSAPI
        
        api = FastBLSAPI()
        indicators = ['cpi', 'ppi']
        
        start_time = time.time()
        data = api.load_multiple(indicators, '2024')
        load_time = (time.time() - start_time) * 1000
        
        success_count = sum(1 for ticker, series_data in data.items() if series_data)
        
        print(f"✅ Multi-indicator test: {success_count}/{len(indicators)} loaded in {load_time:.1f}ms")
        
        for ticker, series_data in data.items():
            if series_data:
                latest = series_data[0]
                print(f"   {ticker.upper()}: {latest['value']} ({latest['date']})")
        
        return success_count > 0
        
    except Exception as e:
        print(f"❌ Multi-indicator test failed: {e}")
        return False

def test_data_validation():
    """Test data validation functions"""
    print("\n🔍 Testing data validation...")
    
    try:
        from app.fast_bls_api import load_data
        
        # Load some data
        data = load_data('cpi', '2024')
        
        if not data:
            print("❌ No data to validate")
            return False
        
        # Basic validation checks
        latest = data[0]
        
        # Check required fields
        required_fields = ['series_id', 'date', 'value', 'year', 'month']
        missing_fields = [field for field in required_fields if field not in latest]
        
        if missing_fields:
            print(f"❌ Missing required fields: {missing_fields}")
            return False
        
        # Check data types
        if not isinstance(latest['value'], (int, float)):
            print("❌ Value field is not numeric")
            return False
        
        if not isinstance(latest['year'], int):
            print("❌ Year field is not integer")
            return False
        
        print("✅ Data validation passed")
        print(f"   Validated {len(data)} data points")
        print(f"   Date range: {data[-1]['date']} to {data[0]['date']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Data validation test failed: {e}")
        return False

def test_cache_files():
    """Test that cache files exist and are readable"""
    print("\n📁 Testing cache files...")
    
    import os
    import json
    
    cache_dir = "cached_data"
    
    if not os.path.exists(cache_dir):
        print(f"❌ Cache directory '{cache_dir}' not found")
        return False
    
    # Look for JSON files
    json_files = [f for f in os.listdir(cache_dir) if f.endswith('.json')]
    
    if not json_files:
        print(f"❌ No JSON cache files found in '{cache_dir}'")
        return False
    
    # Test reading a cache file
    try:
        test_file = os.path.join(cache_dir, json_files[0])
        with open(test_file, 'r') as f:
            cache_data = json.load(f)
        
        print(f"✅ Cache files accessible - found {len(json_files)} files")
        print(f"   Test file: {json_files[0]} ({len(cache_data)} records)")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to read cache file: {e}")
        return False

def main():
    """Run all installation tests"""
    print("🚀 BLS Scraper API - Installation Test")
    print("=" * 50)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    tests = [
        ("Import Test", test_imports),
        ("Cache Files Test", test_cache_files),
        ("Cached API Test", test_cached_api),
        ("Standardized Format Test", test_standardized_format),
        ("Multi-Indicator Test", test_multi_indicator),
        ("Data Validation Test", test_data_validation),
        ("Live Scraper Test", test_live_scraper),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 Test Summary:")
    print("-" * 20)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status:10} {test_name}")
        if result:
            passed += 1
    
    print("-" * 20)
    print(f"Results: {passed}/{total} tests passed ({passed/total*100:.0f}%)")
    
    if passed == total:
        print("\n🎉 All tests passed! Your BLS API installation is working correctly.")
        print("\nNext steps:")
        print("1. Try the demo dashboard: python simple_bls_dashboard.py")
        print("2. See integration examples: python example_integrations.py")
        print("3. Read the documentation: QUICK_START_GUIDE.md")
    elif passed >= total * 0.8:
        print("\n✅ Most tests passed! Your installation is mostly working.")
        print("Some advanced features may not be available, but basic functionality works.")
    else:
        print("\n❌ Many tests failed. Please check your installation.")
        print("Make sure you're in the project root directory and dependencies are installed.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 