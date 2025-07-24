#!/usr/bin/env python3
"""
BLS Data Runner
===============

Downloads the latest BLS data and sets up the environment for using load_data
in other projects and Jupyter notebooks.

Usage:
    python run.py              # Download data and show status
    python run.py --setup      # Download data and set up package
"""

import sys
import logging
from pathlib import Path
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


def download_latest_data():
    """Download the latest BLS data using the scraper"""
    print("🔄 Starting BLS Data Download")
    print("=" * 50)
    
    try:
        from scraper import BLSScraper
        
        # Create scraper and download data
        scraper = BLSScraper()
        success = scraper.run_once()
        
        if success:
            print("✅ Successfully downloaded new data!")
        else:
            print("ℹ️  Data is already up to date")
        
        return True
        
    except Exception as e:
        logger.error(f"Error downloading data: {e}")
        print("❌ Failed to download data")
        return False


def check_data_status():
    """Check what data is available"""
    print("\n📊 Data Status")
    print("=" * 50)
    
    try:
        from config import Config
        
        # Check if data directory exists
        if not Config.DATA_SHEET_DIR.exists():
            print("❌ No data directory found")
            return False
        
        # Find Excel files
        excel_files = list(Config.DATA_SHEET_DIR.glob(Config.EXCEL_FILE_PATTERN))
        
        if not excel_files:
            print("❌ No Excel files found")
            return False
        
        # Show latest file
        latest_file = max(excel_files, key=lambda f: f.stat().st_mtime)
        file_time = datetime.fromtimestamp(latest_file.stat().st_mtime)
        
        print(f"✅ Latest file: {latest_file.name}")
        print(f"📅 Downloaded: {file_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📁 Location: {latest_file}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error checking data status: {e}")
        return False


def test_load_data():
    """Test the load_data function"""
    print("\n🧪 Testing load_data Function")
    print("=" * 50)
    
    try:
        from load_data import load_data
        
        # Test with a few categories
        test_categories = ["All items", "Food", "Energy"]
        data = load_data(test_categories, "2025-06")
        
        if data:
            print(f"✅ Successfully loaded data for {len(data)} categories:")
            for item in data:
                category = item.get('category', 'Unknown')
                nsa_prev = item.get('nsa_previous_month', 'N/A')
                nsa_curr = item.get('nsa_current_month', 'N/A')
                print(f"   📈 {category}: {nsa_prev} → {nsa_curr}")
            return True
        else:
            print("❌ No data returned from load_data")
            return False
            
    except Exception as e:
        logger.error(f"Error testing load_data: {e}")
        print(f"❌ Error testing load_data: {e}")
        return False


def show_usage_instructions():
    """Show how to use the data in other projects"""
    print("\n🚀 How to Use in Other Projects")
    print("=" * 50)
    
    current_dir = Path(__file__).parent.absolute()
    
    print("📋 Method 1: Direct Import (same directory)")
    print(f"   1. Copy bls_package.py to your project folder")
    print(f"   2. In your Python script or Jupyter notebook:")
    print(f"      from bls_package import load_data")
    print(f"      data = load_data(['All items', 'Food'], '2025-06')")
    
    print("\n📋 Method 2: Add to Python Path")
    print(f"   In your Python script or Jupyter notebook:")
    print(f"   import sys")
    print(f"   sys.path.append('{current_dir}')")
    print(f"   from load_data import load_data")
    print(f"   data = load_data(['All items', 'Food'], '2025-06')")
    
    print("\n📋 Method 3: Install as Package")
    print(f"   Run: python setup_package.py")
    print(f"   Then in any project:")
    print(f"   from bls_data import load_data")


def main():
    """Main function"""
    print("🏛️  BLS Data Runner")
    print("=" * 50)
    print("Bureau of Labor Statistics Data Downloader & Setup")
    print()
    
    # Check command line arguments
    setup_mode = "--setup" in sys.argv
    
    # Step 1: Download latest data
    download_success = download_latest_data()
    
    if not download_success:
        print("\n❌ Cannot proceed without data. Check your internet connection.")
        return
    
    # Step 2: Check data status
    data_available = check_data_status()
    
    if not data_available:
        print("\n❌ No data available. Try running the scraper again.")
        return
    
    # Step 3: Test load_data function
    test_success = test_load_data()
    
    if not test_success:
        print("\n❌ load_data function not working properly.")
        return
    
    # Step 4: Show usage instructions
    show_usage_instructions()
    
    # Step 5: Setup package if requested
    if setup_mode:
        print("\n🔧 Setting up package...")
        try:
            import subprocess
            result = subprocess.run([sys.executable, "setup_package.py"], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Package setup complete!")
            else:
                print(f"❌ Package setup failed: {result.stderr}")
        except Exception as e:
            print(f"❌ Could not run setup: {e}")
    
    print("\n✨ Ready to use BLS data in your projects!")
    print("Run 'python run.py --setup' to install as a system package.")


if __name__ == "__main__":
    main()