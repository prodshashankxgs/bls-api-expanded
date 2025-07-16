#!/usr/bin/env python3
"""
Manual FRED Website Scraping Test
Demonstrates scraping https://fred.stlouisfed.org/ directly
"""

import requests
import re
import json
from datetime import datetime
from urllib.parse import urljoin

def scrape_fred_series(series_id="GDP"):
    """Manually scrape FRED series data"""
    print(f"🌐 Scraping FRED series: {series_id}")
    
    # FRED series URL
    url = f"https://fred.stlouisfed.org/series/{series_id}"
    print(f"📍 URL: {url}")
    
    # Headers to appear as a real browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    try:
        # Make request to FRED
        print("📡 Making request to FRED...")
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        print(f"✅ Response received: {response.status_code}")
        print(f"📄 Content length: {len(response.text)} bytes")
        
        # Extract basic information
        html = response.text
        
        # Extract title
        title_match = re.search(r'<title>(.*?)</title>', html)
        title = title_match.group(1) if title_match else "Unknown"
        print(f"📊 Title: {title}")
        
        # Look for data download link
        csv_pattern = r'<a[^>]+href="([^"]*fredgraph\.csv[^"]*)"'
        csv_match = re.search(csv_pattern, html)
        
        if csv_match:
            csv_url = csv_match.group(1)
            if not csv_url.startswith('http'):
                csv_url = urljoin(url, csv_url)
            
            print(f"📥 Found CSV download: {csv_url}")
            
            # Download CSV data
            print("📊 Downloading CSV data...")
            csv_response = requests.get(csv_url, headers=headers, timeout=10)
            csv_response.raise_for_status()
            
            # Parse CSV data
            csv_data = csv_response.text
            lines = csv_data.strip().split('\n')
            
            print(f"📈 CSV data received: {len(lines)} lines")
            
            if len(lines) > 1:
                print("📋 Sample data:")
                print(f"   Header: {lines[0]}")
                if len(lines) > 1:
                    print(f"   First row: {lines[1]}")
                if len(lines) > 2:
                    print(f"   Last row: {lines[-1]}")
                
                # Count valid data points
                data_points = 0
                for line in lines[1:]:  # Skip header
                    parts = line.split(',')
                    if len(parts) >= 2 and parts[1].strip() not in ['', '.', 'NA']:
                        data_points += 1
                
                print(f"📊 Valid data points: {data_points}")
                
                return {
                    "series_id": series_id,
                    "title": title,
                    "url": url,
                    "csv_url": csv_url,
                    "data_points": data_points,
                    "sample_data": lines[:3],
                    "scraped_at": datetime.now().isoformat(),
                    "success": True
                }
        else:
            print("❌ No CSV download link found")
            
            # Look for JSON data in script tags
            script_pattern = r'<script[^>]*>(.*?)</script>'
            scripts = re.findall(script_pattern, html, re.DOTALL)
            
            json_found = False
            for script in scripts:
                if 'chartData' in script or 'seriesData' in script:
                    print("📊 Found potential chart data in script")
                    json_found = True
                    break
            
            if not json_found:
                print("⚠️  No obvious data sources found in HTML")
            
            return {
                "series_id": series_id,
                "title": title,
                "url": url,
                "success": False,
                "error": "No CSV download found",
                "scraped_at": datetime.now().isoformat()
            }
            
    except requests.exceptions.RequestException as e:
        print(f"🚨 Network error: {e}")
        return {
            "series_id": series_id,
            "success": False,
            "error": str(e),
            "scraped_at": datetime.now().isoformat()
        }
    except Exception as e:
        print(f"🚨 Scraping error: {e}")
        return {
            "series_id": series_id,
            "success": False,
            "error": str(e),
            "scraped_at": datetime.now().isoformat()
        }

def test_multiple_series():
    """Test scraping multiple FRED series"""
    series_list = ["GDP", "UNRATE", "CPIAUCSL", "FEDFUNDS"]
    
    print("🚀 Testing Multiple FRED Series")
    print("=" * 50)
    
    results = []
    for series_id in series_list:
        print(f"\n📈 Testing {series_id}...")
        result = scrape_fred_series(series_id)
        results.append(result)
        
        if result["success"]:
            print(f"✅ {series_id}: SUCCESS")
        else:
            print(f"❌ {series_id}: FAILED - {result.get('error', 'Unknown error')}")
    
    # Summary
    successful = sum(1 for r in results if r["success"])
    print(f"\n📊 Summary: {successful}/{len(results)} series scraped successfully")
    
    return results

if __name__ == "__main__":
    print("🌐 Manual FRED Website Scraping Test")
    print("=" * 50)
    print("🎯 Target: https://fred.stlouisfed.org/")
    print(f"⏰ Started: {datetime.now()}")
    
    # Test single series
    print("\n1️⃣ Testing Single Series (GDP):")
    result = scrape_fred_series("GDP")
    
    print(f"\n📋 Result:")
    print(json.dumps(result, indent=2, default=str))
    
    # Test multiple series
    print("\n2️⃣ Testing Multiple Series:")
    results = test_multiple_series()
    
    print(f"\n⏰ Completed: {datetime.now()}")
    print("\n✅ Manual scraping test completed!")
    print("🔧 This shows the FRED website is accessible and scrapeable")
    print("🎯 The full Scrapy system can be configured to use this approach") 