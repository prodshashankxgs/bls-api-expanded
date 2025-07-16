#!/usr/bin/env python3
"""
Quick test script for BLS MVP API
Run this while your server is running on localhost:8000
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"


def test_endpoint(endpoint, description):
    """Test a single endpoint and show results"""
    print(f"\n{'=' * 50}")
    print(f"Testing: {description}")
    print(f"URL: {BASE_URL}{endpoint}")
    print('=' * 50)

    try:
        start_time = time.time()
        response = requests.get(f"{BASE_URL}{endpoint}", timeout=30)
        duration = time.time() - start_time

        print(f"Status Code: {response.status_code}")
        print(f"Response Time: {duration:.2f} seconds")

        if response.status_code == 200:
            data = response.json()
            print("✅ SUCCESS!")

            # Pretty print the response (limited)
            if isinstance(data, dict):
                if 'data' in data and isinstance(data['data'], list):
                    print(f"Data Points: {len(data['data'])}")
                    if data['data']:
                        latest = data['data'][0]
                        print(f"Latest Value: {latest.get('value')} ({latest.get('date')})")
                        if latest.get('month_change'):
                            print(f"Month Change: {latest.get('month_change'):.2f}%")
                        if latest.get('trend'):
                            print(f"Trend: {latest.get('trend')}")

                if 'series_name' in data:
                    print(f"Series: {data['series_name']} - {data.get('title', '')}")
                    print(f"Units: {data.get('units', '')}")
                    if data.get('cached'):
                        print("🚀 CACHED RESPONSE (Fast!)")

                if 'latest_values' in data:
                    print(f"Latest Values: {data['latest_values']}")

                if 'indicators' in data:
                    print("Dashboard Indicators:")
                    for name, info in data['indicators'].items():
                        if 'value' in info:
                            print(f"  {name}: {info['value']} {info.get('units', '')}")

            # Show a sample of the JSON (first 500 chars)
            json_str = json.dumps(data, indent=2, default=str)
            if len(json_str) > 500:
                print(f"\nSample Response:\n{json_str[:500]}...")
            else:
                print(f"\nFull Response:\n{json_str}")

        else:
            print(f"❌ ERROR: {response.status_code}")
            print(f"Response: {response.text}")

    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Cannot connect to server. Is it running on localhost:8000?")
        print("Start server with: uvicorn app.main:app --reload")
    except requests.exceptions.Timeout:
        print("❌ ERROR: Request timed out")
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")


def main():
    print("🚀 Testing BLS MVP API")
    print("Make sure your server is running: uvicorn app.main:app --reload")

    # Test basic endpoints
    test_endpoint("/", "Root endpoint")
    test_endpoint("/health", "Health check")
    test_endpoint("/series", "Available series list")

    # Test data endpoints
    test_endpoint("/data/unemployment", "Unemployment data (enhanced)")
    test_endpoint("/data/unemployment?enhanced=false", "Unemployment data (basic)")
    test_endpoint("/data/inflation?years=2", "Inflation data (2 years)")
    test_endpoint("/data/wages", "Wage data")

    # Test caching (run same request twice)
    print(f"\n{'=' * 50}")
    print("Testing Cache Performance")
    print('=' * 50)

    print("First request (should be slower):")
    test_endpoint("/data/jobs", "Jobs data - First Request")

    print("\nSecond request (should be faster - cached):")
    test_endpoint("/data/jobs", "Jobs data - Cached Request")

    # Test comparison
    test_endpoint("/compare?series1=unemployment&series2=inflation", "Compare unemployment vs inflation")

    # Test dashboard
    test_endpoint("/dashboard", "Economic dashboard")

    # Test cache status
    test_endpoint("/cache/status", "Cache status")

    # Test error handling
    test_endpoint("/data/invalid_series", "Error handling test")

    print(f"\n{'=' * 50}")
    print("✅ Testing Complete!")
    print("If you see BLS data with calculated fields, your API is working!")
    print("Key features tested:")
    print("  ✓ Real BLS data fetching")
    print("  ✓ Enhanced calculations (month change, trends)")
    print("  ✓ Caching for performance")
    print("  ✓ Multi-series comparison")
    print("  ✓ Economic dashboard")
    print("  ✓ Error handling")
    print('=' * 50)


if __name__ == "__main__":
    main()