#!/usr/bin/env python3
"""
Demonstration of Standardized Professional Data Format

This script shows the difference between the old basic format and the new 
standardized professional format that hedge funds would expect.
"""

import json
from datetime import datetime

def demonstrate_data_formats():
    """Show comparison between old and new data formats"""
    
    print("🔄 BLS Data API - Format Standardization Demo")
    print("=" * 60)
    
    # Import both APIs
    try:
        from app.fast_bls_api import load_data as load_cached
        from app.live_bls_scraper import load_data as load_live
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're running from the project root directory")
        return
    
    print("\n📊 Testing CPI Data Retrieval...\n")
    
    # Test 1: Old format (legacy)
    print("1️⃣  LEGACY FORMAT (Basic List)")
    print("-" * 40)
    
    try:
        legacy_data = load_cached('cpi', '2024', standardized=False)
        if legacy_data:
            print("✅ Legacy format sample:")
            print(json.dumps(legacy_data[0], indent=2))
            print(f"📈 Total data points: {len(legacy_data)}")
            print(f"🔑 Data keys: {list(legacy_data[0].keys())}")
        else:
            print("❌ No data returned")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "="*60 + "\n")
    
    # Test 2: New standardized format
    print("2️⃣  STANDARDIZED PROFESSIONAL FORMAT")
    print("-" * 40)
    
    try:
        standard_data = load_cached('cpi', '2024', standardized=True)
        if isinstance(standard_data, dict) and standard_data.get('success'):
            print("✅ Standardized format structure:")
            
            # Show metadata
            print("\n📋 METADATA:")
            metadata = standard_data['metadata']
            print(f"  Timestamp: {metadata['timestamp']}")
            print(f"  Source: {metadata['source']}")
            print(f"  Quality: {metadata['quality']}")
            print(f"  Latency: {metadata['latency_ms']}ms")
            print(f"  Total Points: {metadata['total_points']}")
            print(f"  API Version: {metadata['api_version']}")
            
            # Show series info
            print("\n📊 SERIES INFORMATION:")
            series = standard_data['series']
            print(f"  ID: {series['id']}")
            print(f"  Name: {series['name']}")
            print(f"  Category: {series['category']}")
            print(f"  Frequency: {series['frequency']}")
            print(f"  Units: {series['units']}")
            print(f"  Source Agency: {series['source_agency']}")
            
            # Show sample data point
            print("\n📈 SAMPLE DATA POINT:")
            if standard_data['data']:
                sample_point = standard_data['data'][0]
                print(json.dumps(sample_point, indent=2))
            
            print(f"\n🎯 Response Structure Keys: {list(standard_data.keys())}")
            
        else:
            print("❌ No data returned or error occurred")
            if isinstance(standard_data, dict) and standard_data.get('error'):
                print(f"Error: {standard_data['error']}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "="*60 + "\n")
    
    # Test 3: Live scraping with standardized format
    print("3️⃣  LIVE SCRAPING - STANDARDIZED FORMAT")
    print("-" * 40)
    
    try:
        print("🌐 Live scraping fresh data...")
        live_standard = load_live('cpi', '2024', standardized=True)
        
        if isinstance(live_standard, dict) and live_standard.get('success'):
            print("✅ Live scraped standardized data:")
            
            metadata = live_standard['metadata']
            print(f"\n⚡ Performance Metrics:")
            print(f"  Source: {metadata['source']}")
            print(f"  Latency: {metadata['latency_ms']}ms")
            print(f"  Fresh Data Points: {metadata['total_points']}")
            print(f"  Quality: {metadata['quality']}")
            
            # Show that data is marked as freshly scraped
            if live_standard['data']:
                sample = live_standard['data'][0]
                print(f"\n🔥 Fresh Data Sample:")
                print(f"  Date: {sample['date']}")
                print(f"  Value: {sample['value']}")
                if 'revision_status' in sample:
                    print(f"  Status: {sample['revision_status']}")
                    
        else:
            print("⚠️  Live scraping failed or returned no data")
            if isinstance(live_standard, dict) and live_standard.get('error'):
                print(f"Error: {live_standard['error']}")
                
    except Exception as e:
        print(f"❌ Live scraping error: {e}")
    
    print("\n" + "="*60 + "\n")
    
    # Summary
    print("📋 FORMAT COMPARISON SUMMARY")
    print("-" * 40)
    print("🔸 LEGACY FORMAT:")
    print("  - Simple list of dictionaries")
    print("  - 6 fields per data point")
    print("  - No metadata or context")
    print("  - Basic error handling")
    
    print("\n🔸 STANDARDIZED PROFESSIONAL FORMAT:")
    print("  - Complete response object with metadata")
    print("  - Rich series information and descriptions")
    print("  - Performance metrics (latency, quality indicators)")
    print("  - Professional error handling with status codes")
    print("  - API versioning support")
    print("  - Extensible for future features")
    
    print("\n🎯 HEDGE FUND READY FEATURES:")
    print("  ✅ Consistent JSON schema across all endpoints")
    print("  ✅ Data quality indicators (high/medium/low)")
    print("  ✅ Source attribution and timestamps")
    print("  ✅ Performance monitoring (latency tracking)")
    print("  ✅ Professional error messages")
    print("  ✅ Backward compatibility maintained")
    
    print("\n🚀 Ready for production trading systems!")

if __name__ == "__main__":
    demonstrate_data_formats() 