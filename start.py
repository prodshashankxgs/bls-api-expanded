#!/usr/bin/env python3
"""
BLS Scraper - Simple Startup Script
Run this to start the API server in the background for easy data access
"""

import subprocess
import sys
import time
import requests
from pathlib import Path

def check_dependencies():
    """Check if required packages are installed"""
    try:
        import flask
        import requests
        import beautifulsoup4
        print("✅ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Run: pip install -r requirements.txt")
        return False

def check_port_available(port=5000):
    """Check if port is available"""
    try:
        response = requests.get(f"http://localhost:{port}/health", timeout=2)
        print(f"⚠️  Port {port} already in use - API might already be running!")
        print(f"✅ API is healthy: {response.json().get('status', 'unknown')}")
        return False
    except requests.exceptions.ConnectionError:
        return True
    except Exception:
        return True

def start_api_server():
    """Start the API server"""
    print("🚀 Starting BLS Scraper API server...")
    
    if not check_dependencies():
        return False
    
    if not check_port_available():
        choice = input("Continue anyway? (y/n): ").lower()
        if choice != 'y':
            return False
    
    try:
        # Start the server
        print("📡 Starting server at http://localhost:5000")
        subprocess.run([sys.executable, "app.py"], check=True)
    except KeyboardInterrupt:
        print("\n⏹️  Server stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start server: {e}")
        return False
    except FileNotFoundError:
        print("❌ app.py not found. Make sure you're in the correct directory.")
        return False
    
    return True

def quick_test():
    """Quick test of the API"""
    print("\n🧪 Testing API endpoints...")
    
    base_url = "http://localhost:5000"
    tests = [
        ("/health", "Health check"),
        ("/indicators", "Available indicators"),
        ("/data/cpi?date=2024", "CPI data sample")
    ]
    
    for endpoint, description in tests:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            if response.status_code == 200:
                print(f"✅ {description}: OK")
            else:
                print(f"⚠️  {description}: HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ {description}: {e}")

if __name__ == "__main__":
    print("🌐 BLS Economic Data Scraper")
    print("="*50)
    
    # Check if we're in the right directory
    if not Path("app.py").exists():
        print("❌ app.py not found!")
        print("Make sure you're in the BLS-Scraper-API directory")
        sys.exit(1)
    
    print("Starting API server... (Ctrl+C to stop)")
    success = start_api_server()
    
    if success:
        print("\n" + "="*50)
        print("✅ API server ready!")
        print("📖 Use: http://localhost:5000/data/cpi?date=2022-2024")
        print("💻 In your code: requests.get('http://localhost:5000/data/cpi')")