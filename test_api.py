#!/usr/bin/env python3
"""
Quick API Test - Verify the BLS Scraper API is working correctly
Run this after starting the API server to test all functionality
"""

import requests
import json
import time
from datetime import datetime

API_BASE = "http://localhost:5000"

def test_endpoint(endpoint, description, expected_keys=None):
    """Test a single API endpoint"""
    try:
        print(f"🧪 Testing {description}...")
        
        start_time = time.time()
        response = requests.get(f"{API_BASE}{endpoint}", timeout=30)
        response_time = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            
            # Check expected keys if provided
            if expected_keys:
                missing_keys = [key for key in expected_keys if key not in data]
                if missing_keys:
                    print(f"   ⚠️  Missing keys: {missing_keys}")
                    return False
            
            print(f"   ✅ Success ({response_time:.2f}s)")
            
            # Print sample data
            if 'data' in data and data['data']:
                sample = data['data'][0]
                if 'value' in sample and 'date' in sample:
                    print(f"   📊 Sample: {sample['value']} on {sample['date']}")
            elif 'indicators' in data:
                count = len(data['indicators'])
                print(f"   📋 Found {count} indicators")
            elif 'status' in data:
                print(f"   🔋 Status: {data['status']}")
            
            return True
            
        else:
            print(f"   ❌ HTTP {response.status_code}: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"   ❌ Connection failed - is the API server running?")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_data_quality(data):
    """Test the quality of returned data"""
    if not data or 'data' not in data:
        return False
    
    items = data['data']
    if not items:
        return False
    
    # Check first item has required fields
    first_item = items[0]
    required_fields = ['series_id', 'date', 'value', 'year']
    
    for field in required_fields:
        if field not in first_item:
            print(f"   ❌ Missing required field: {field}")
            return False
    
    # Check data types
    if not isinstance(first_item['value'], (int, float)):
        print(f"   ❌ Value should be numeric, got: {type(first_item['value'])}")
        return False
    
    if not isinstance(first_item['year'], int):
        print(f"   ❌ Year should be integer, got: {type(first_item['year'])}")
        return False
    
    print(f"   ✅ Data quality check passed ({len(items)} items)")
    return True

def main():
    """Run comprehensive API tests"""
    print("🧪 BLS Scraper API - Comprehensive Test Suite")
    print("="*60)
    print(f"Testing API at: {API_BASE}")
    print(f"Test time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    tests_passed = 0
    total_tests = 0
    
    # Test 1: Health check
    total_tests += 1
    if test_endpoint("/health", "Health check", ["status", "timestamp"]):
        tests_passed += 1
    
    print()
    
    # Test 2: Available indicators
    total_tests += 1
    if test_endpoint("/indicators", "Available indicators", ["indicators", "status"]):
        tests_passed += 1
    
    print()
    
    # Test 3: CPI data
    total_tests += 1
    print("🧪 Testing CPI data...")
    try:
        response = requests.get(f"{API_BASE}/data/cpi?date=2023-2024", timeout=30)
        if response.status_code == 200:
            data = response.json()
            if test_data_quality(data):
                print("   ✅ CPI data test passed")
                tests_passed += 1
            else:
                print("   ❌ CPI data quality check failed")
        else:
            print(f"   ❌ CPI data request failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ CPI data test error: {e}")
    
    print()
    
    # Test 4: Unemployment data  
    total_tests += 1
    print("🧪 Testing unemployment data...")
    try:
        response = requests.get(f"{API_BASE}/data/unemployment?date=2024", timeout=30)
        if response.status_code == 200:
            data = response.json()
            if test_data_quality(data):
                print("   ✅ Unemployment data test passed")
                tests_passed += 1
            else:
                print("   ❌ Unemployment data quality check failed")
        else:
            print(f"   ❌ Unemployment data request failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Unemployment data test error: {e}")
    
    print()
    
    # Test 5: CSV format
    total_tests += 1
    print("🧪 Testing CSV output format...")
    try:
        response = requests.get(f"{API_BASE}/data/cpi?date=2024&format=csv", timeout=30)
        if response.status_code == 200 and 'text/csv' in response.headers.get('content-type', ''):
            if 'series_id' in response.text and 'value' in response.text:
                print("   ✅ CSV format test passed")
                tests_passed += 1
            else:
                print("   ❌ CSV content validation failed")
        else:
            print(f"   ❌ CSV format test failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ CSV format test error: {e}")
    
    # Results summary
    print("\n" + "="*60)
    print(f"🏆 TEST RESULTS: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("✅ ALL TESTS PASSED! API is working correctly.")
        print("\n🚀 Your colleague can now use:")
        print("   • requests.get('http://localhost:5000/data/cpi?date=2022-2024')")
        print("   • requests.get('http://localhost:5000/data/unemployment?date=2023')")
    elif tests_passed >= total_tests * 0.8:
        print("⚠️  Most tests passed. API is mostly functional.")
    else:
        print("❌ Several tests failed. Check the API server and logs.")
    
    return tests_passed == total_tests

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)