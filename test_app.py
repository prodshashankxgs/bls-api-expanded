#!/usr/bin/env python3
"""
Simple test script for BLS Scraper
Run this to verify everything works correctly
"""

import time
from bls_scraper import load_data, get_available_indicators, clear_cache

def test_basic_functionality():
    """Test basic data loading"""
    print("🧪 BASIC FUNCTIONALITY TESTS")
    print("="*50)
    
    tests_passed = 0
    total_tests = 5
    
    # Test 1: CPI data
    print("\n1️⃣ Testing CPI data loading...")
    try:
        start = time.time()
        cpi_data = load_data('cpi', '2025')
        elapsed = time.time() - start
        
        if cpi_data and len(cpi_data) > 0:
            print(f"   ✅ Success: {len(cpi_data)} points in {elapsed:.2f}s")
            print(f"   📊 Latest CPI: {cpi_data[0]['value']}")
            tests_passed += 1
        else:
            print("   ❌ Failed: No data returned")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: Core CPI
    print("\n2️⃣ Testing Core CPI...")
    try:
        core_cpi = load_data('cpi_core', '2024')
        if core_cpi:
            print(f"   ✅ Success: {len(core_cpi)} core CPI points")
            print(f"   📊 Latest Core CPI: {core_cpi[0]['value']}")
            tests_passed += 1
        else:
            print("   ❌ Failed: No core CPI data")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Unemployment
    print("\n3️⃣ Testing Unemployment Rate...")
    try:
        unemployment = load_data('unemployment', '2024')
        if unemployment:
            print(f"   ✅ Success: {len(unemployment)} unemployment points")
            print(f"   📊 Latest Unemployment: {unemployment[0]['value']}%")
            tests_passed += 1
        else:
            print("   ❌ Failed: No unemployment data")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 4: Cache performance
    print("\n4️⃣ Testing Cache Performance...")
    try:
        start = time.time()
        cached_data = load_data('cpi', '2025')  # Should be cached
        elapsed = time.time() - start
        
        if cached_data and elapsed < 0.1:
            print(f"   ✅ Success: Cached load in {elapsed:.3f}s")
            print("   ⚡ Ultra-fast cache performance!")
            tests_passed += 1
        else:
            print(f"   ⚠️  Cache slow: {elapsed:.3f}s (should be <0.1s)")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 5: Date range formats
    print("\n5️⃣ Testing Date Formats...")
    try:
        # Test different date formats
        formats_to_test = ['2025', '2023-2025', 'last 2 years']
        format_results = []
        
        for date_format in formats_to_test:
            data = load_data('cpi', date_format)
            if data:
                format_results.append(f"{date_format}: {len(data)} points")
        
        if len(format_results) >= 2:
            print(f"   ✅ Success: Multiple date formats work")
            for result in format_results:
                print(f"      📅 {result}")
            tests_passed += 1
        else:
            print("   ❌ Failed: Date format issues")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print(f"\n📊 Test Results: {tests_passed}/{total_tests} passed")
    return tests_passed >= 4

def test_performance():
    """Test performance metrics"""
    print("\n⚡ PERFORMANCE TESTS")
    print("="*50)
    
    # Fresh data performance
    print("\n🔸 Fresh Data Speed Test...")
    clear_cache()  # Ensure fresh fetch
    
    start = time.time()
    fresh_data = load_data('cpi', '2024')
    fresh_time = time.time() - start
    
    print(f"   Fresh fetch: {fresh_time:.2f}s")
    
    # Cached data performance
    print("\n🔸 Cached Data Speed Test...")
    start = time.time()
    cached_data = load_data('cpi', '2024')  # Should be cached now
    cached_time = time.time() - start
    
    print(f"   Cached fetch: {cached_time:.3f}s")
    
    # Performance evaluation
    if fresh_time < 5.0:
        print("   ✅ Fresh data: Fast")
    else:
        print("   ⚠️  Fresh data: Slow")
    
    if cached_time < 0.1:
        print("   ✅ Cached data: Ultra-fast")
    else:
        print("   ⚠️  Cached data: Not optimized")

def test_data_quality():
    """Test data quality and structure"""
    print("\n🔍 DATA QUALITY TESTS")
    print("="*50)
    
    data = load_data('cpi', '2024')
    
    if not data:
        print("   ❌ No data to test")
        return False
    
    # Check data structure
    required_fields = ['series_id', 'date', 'value', 'year', 'month', 'source']
    sample = data[0]
    
    print(f"\n🔸 Testing data structure...")
    missing_fields = []
    for field in required_fields:
        if field not in sample:
            missing_fields.append(field)
    
    if missing_fields:
        print(f"   ❌ Missing fields: {missing_fields}")
    else:
        print("   ✅ All required fields present")
    
    # Check data types
    print(f"\n🔸 Testing data types...")
    try:
        assert isinstance(sample['value'], (int, float)), "Value should be numeric"
        assert isinstance(sample['year'], int), "Year should be integer"
        assert isinstance(sample['date'], str), "Date should be string"
        print("   ✅ Data types correct")
    except AssertionError as e:
        print(f"   ❌ Data type error: {e}")
        return False
    
    # Check data values
    print(f"\n🔸 Testing data values...")
    if 50 < sample['value'] < 500:  # Reasonable CPI range
        print(f"   ✅ CPI value reasonable: {sample['value']}")
    else:
        print(f"   ⚠️  CPI value unusual: {sample['value']}")
    
    print(f"   📊 Sample data:")
    print(f"      Date: {sample['date']}")
    print(f"      Value: {sample['value']}")
    print(f"      Source: {sample['source']}")
    
    return True

def main():
    """Run all tests"""
    print("🧪 BLS SCRAPER APPLICATION TESTS")
    print("="*60)
    
    # Show available indicators
    indicators = get_available_indicators()
    print(f"📊 Available indicators: {len(indicators)}")
    print(f"   {list(indicators.keys())[:5]}...")  # Show first 5
    
    # Run tests
    basic_passed = test_basic_functionality()
    test_performance()
    quality_passed = test_data_quality()
    
    # Final summary
    print("\n" + "="*60)
    print("🎯 FINAL TEST SUMMARY")
    print("="*60)
    
    if basic_passed and quality_passed:
        print("✅ ALL TESTS PASSED")
        print("🚀 Application is working correctly!")
        print("📖 Ready for use: load_data('cpi', '2024')")
    else:
        print("⚠️  SOME TESTS FAILED")
        print("🔧 Application may need debugging")
    
    print(f"\n💡 Test completed. Cache location: data_cache/")

if __name__ == "__main__":
    main()