#!/usr/bin/env python3
"""
BLS Auto-Scraper - Continuous Data Updates
==========================================

This script continuously monitors for new BLS Excel files and keeps your data fresh.
Perfect for running in one VSCode tab while you work with the data in another.

Features:
- Automatic detection of new BLS Excel releases
- Smart download scheduling (checks every hour during business days)
- Real-time data processing and validation
- Status dashboard with live updates
- Seamless integration with your load_data() functions

Usage:
    python3 auto_scraper.py
    
Then in another VSCode tab/window:
    from data_loader import load_data
    df = load_data("CPSCJEWE Index", "latest")
"""

import asyncio
import schedule
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List
import sys
import signal

from xlsx_loader import BLSExcelDownloader, ExcelDataProcessor
from data_loader import read_excel_with_named_columns, get_all_tickers

# Configure logging for nice output
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

class BLSAutoScraper:
    """
    Automatic BLS data scraper that runs continuously
    """
    
    def __init__(self):
        """Initialize the auto-scraper"""
        self.downloader = BLSExcelDownloader()
        self.processor = ExcelDataProcessor()
        self.running = False
        self.last_check = None
        self.last_download = None
        self.current_files = set()
        self.stats = {
            'total_checks': 0,
            'successful_downloads': 0,
            'data_points_processed': 0,
            'last_update': None
        }
        
        # Setup graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        print("\nShutting down auto-scraper...")
        self.running = False
        sys.exit(0)
    
    def print_banner(self):
        """Print startup banner"""
        print("BLS AUTO-SCRAPER")
        print("=" * 50)
        print("Monitoring BLS for new Excel files...")
        print("Your data will be automatically updated!")
        print("Keep this tab running, use data in another tab")
        print("Checks every hour during business hours")
        print("Real-time processing and validation")
        print("=" * 50)
        print()
    
    def get_current_files(self) -> set:
        """Get current Excel files in data_sheet directory"""
        try:
            data_sheet_path = Path("data_sheet")
            if not data_sheet_path.exists():
                return set()
            
            return {f.name for f in data_sheet_path.glob("*.xlsx")}
        except Exception as e:
            logger.error(f"Error getting current files: {e}")
            return set()
    
    def check_for_updates(self) -> bool:
        """
        Check for new BLS Excel files
        
        Returns:
            True if new files were found and downloaded
        """
        try:
            logger.info("🔍 Checking BLS website for new files...")
            self.stats['total_checks'] += 1
            self.last_check = datetime.now()
            
            # Get current files before checking
            files_before = self.current_files.copy()
            
            # Try to download latest file
            latest_file = self.downloader.download_latest_cpi_file()
            
            if latest_file:
                # Update current files
                self.current_files = self.get_current_files()
                
                # Check if we got a new file
                new_files = self.current_files - files_before
                
                if new_files:
                    logger.info(f"New file downloaded: {', '.join(new_files)}")
                    self.stats['successful_downloads'] += 1
                    self.last_download = datetime.now()
                    
                    # Process the new file
                    self.process_new_file(latest_file)
                    return True
                else:
                    logger.info("No new files - data is up to date")
                    return False
            else:
                logger.warning("Failed to download files from BLS")
                return False
                
        except Exception as e:
            logger.error(f"Error checking for updates: {e}")
            return False
    
    def process_new_file(self, file_path: Path):
        """Process a newly downloaded Excel file"""
        try:
            logger.info(f"Processing new file: {file_path.name}")
            
            # Read and validate the file
            df = read_excel_with_named_columns(file_path)
            
            if not df.is_empty():
                self.stats['data_points_processed'] = df.shape[0]
                self.stats['last_update'] = datetime.now()
                
                logger.info(f"Processed {df.shape[0]} rows, {df.shape[1]} columns")
                
                # Validate key indicators are present
                self.validate_data(df)
                
                # Update user
                self.print_data_summary(df)
                
            else:
                logger.warning("Downloaded file appears to be empty")
                
        except Exception as e:
            logger.error(f"Error processing file: {e}")
    
    def validate_data(self, df) -> bool:
        """Validate that key economic indicators are available"""
        try:
            key_indicators = [
                "All items",
                "All items less food and energy", 
                "Food",
                "Energy"
            ]
            
            found_indicators = []
            
            if 'expenditure_category' in df.columns:
                for indicator in key_indicators:
                    matches = df.filter(
                        df['expenditure_category'].str.contains(indicator, literal=False)
                    )
                    if not matches.is_empty():
                        found_indicators.append(indicator)
            
            if found_indicators:
                logger.info(f"Validated {len(found_indicators)}/{len(key_indicators)} key indicators")
                return True
            else:
                logger.warning("Could not validate key indicators in data")
                return False
                
        except Exception as e:
            logger.error(f"Error validating data: {e}")
            return False
    
    def print_data_summary(self, df):
        """Print a nice summary of the processed data"""
        try:
            print()
            print("DATA UPDATE SUMMARY")
            print("-" * 30)
            
            # Basic stats
            print(f"Total categories: {df.shape[0]}")
            print(f"Data columns: {df.shape[1]}")
            
            # Show some key categories if available
            if 'expenditure_category' in df.columns and 'relative_importance_pct' in df.columns:
                print("Key Categories Available:")
                
                key_items = [
                    "All items",
                    "All items less food and energy",
                    "Food", 
                    "Energy"
                ]
                
                for item in key_items:
                    matches = df.filter(
                        df['expenditure_category'].str.contains(item, literal=False)
                    )
                    if not matches.is_empty():
                        first_match = matches.head(1)
                        for row in first_match.iter_rows(named=True):
                            weight = row.get('relative_importance_pct', 'N/A')
                            print(f"   ✓ {item:<35} (Weight: {weight}%)")
            
            print(f"Ready for use! Try: load_data('CPSCJEWE Index', 'latest')")
            print("-" * 50)
            print()
            
        except Exception as e:
            logger.error(f"Error printing summary: {e}")
    
    def print_status(self):
        """Print current status dashboard"""
        try:
            print("AUTO-SCRAPER STATUS DASHBOARD")
            print("=" * 40)
            print(f"Running: {'Yes' if self.running else 'No'}")
            print(f"Last Check: {self.last_check.strftime('%H:%M:%S') if self.last_check else 'Never'}")
            print(f"Last Download: {self.last_download.strftime('%H:%M:%S') if self.last_download else 'Never'}")
            print(f"Current Files: {len(self.current_files)}")
            print(f"Total Checks: {self.stats['total_checks']}")
            print(f"Downloads: {self.stats['successful_downloads']}")
            print(f"Data Points: {self.stats['data_points_processed']}")
            
            if self.stats['last_update']:
                print(f"Last Update: {self.stats['last_update'].strftime('%H:%M:%S')}")
            
            print()
            print("Available Tickers for load_data():")
            tickers = get_all_tickers()[:8]  # Show first 8
            for i, ticker in enumerate(tickers):
                print(f"   {ticker}")
                if i >= 7:
                    print(f"   ... and {len(get_all_tickers()) - 8} more")
                    break
            
            print()
            print("Usage in other tab:")
            print("   from data_loader import load_data")
            print("   df = load_data('CPSCJEWE Index', 'latest')")
            print("=" * 40)
            print()
            
        except Exception as e:
            logger.error(f"Error printing status: {e}")
    
    def schedule_checks(self):
        """Set up the checking schedule"""
        # Check every hour during business hours (9 AM - 6 PM ET)
        for hour in range(9, 19):  # 9 AM to 6 PM
            schedule.every().day.at(f"{hour:02d}:00").do(self.check_for_updates)
            schedule.every().day.at(f"{hour:02d}:30").do(self.check_for_updates)  # Also check at half hour
        
        # Also check at startup
        schedule.every().monday.at("08:30").do(self.check_for_updates)
        schedule.every().tuesday.at("08:30").do(self.check_for_updates)
        schedule.every().wednesday.at("08:30").do(self.check_for_updates)
        schedule.every().thursday.at("08:30").do(self.check_for_updates)
        schedule.every().friday.at("08:30").do(self.check_for_updates)
        
        logger.info("Scheduled checks every 30 minutes during business hours")
    
    def run(self):
        """Main run loop"""
        self.running = True
        self.print_banner()
        
        # Initialize current files
        self.current_files = self.get_current_files()
        logger.info(f"Found {len(self.current_files)} existing Excel files")
        
        # Schedule checks
        self.schedule_checks()
        
        # Do an initial check
        logger.info("Performing initial check...")
        self.check_for_updates()
        
        # Print initial status
        self.print_status()
        
        # Main loop
        try:
            while self.running:
                # Run scheduled jobs
                schedule.run_pending()
                
                # Sleep for a minute
                time.sleep(60)
                
                # Print status every 10 minutes
                if datetime.now().minute % 10 == 0:
                    self.print_status()
                    
        except KeyboardInterrupt:
            logger.info("Received shutdown signal")
        finally:
            self.running = False
            print("Auto-scraper stopped. Your data remains available!")

def main():
    """Main entry point"""
    scraper = BLSAutoScraper()
    scraper.run()

if __name__ == "__main__":
    main() 