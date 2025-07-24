#!/usr/bin/env python3
"""
BLS Scraper - Economic Data Downloader
=======================================

Downloads Excel files from the Bureau of Labor Statistics and extracts CPI data.
Cross-platform compatible and easy to understand.

Usage:
    python scraper.py              # Run once
    python scraper.py continuous   # Run continuously  
    python scraper.py data         # Get data and show sample
"""

import time
import logging
from datetime import datetime
from pathlib import Path
import pandas as pd
from config import Config

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


class BLSScraper:
    """BLS data scraper"""
    
    def __init__(self):
        """Initialize the scraper"""
        logger.info("starting bls scraper")
        
        # make sure our directories exist
        self.setup_directories()
        
        # import the components we need
        from xlsx_loader import BLSExcelDownloader, ExcelDataProcessor
        
        self.downloader = BLSExcelDownloader()
        self.processor = ExcelDataProcessor()
        
        # keep track of what we've done
        self.files_downloaded = 0
        self.last_check = None
        self.last_download = None
        
        logger.info("scraper ready")
    
    def setup_directories(self):
        """Make sure all our directories exist"""
        try:
            Config.ensure_directories_exist()
            logger.info(f"data directory: {Config.DATA_SHEET_DIR}")
            logger.info(f"cache directory: {Config.CACHE_DIR}")
        except Exception as e:
            logger.error(f"could not create directories: {e}")
            raise
    
    def check_for_new_files(self):
        """Check if there are new Excel files to download"""
        logger.info("checking bls website for new files")
        start_time = time.time()
        
        try:
            # get current files before checking
            old_files = self.get_current_files()
            logger.info(f"currently have {len(old_files)} excel files")
            
            # try to download the latest file
            new_file = self.downloader.download_latest_cpi_file()
            
            # check what we got
            if new_file:
                new_files = self.get_current_files()
                if len(new_files) > len(old_files):
                    self.files_downloaded += 1
                    self.last_download = datetime.now()
                    download_time = time.time() - start_time
                    
                    logger.info(f"downloaded new file: {new_file.name}")
                    logger.info(f"download took {download_time:.2f} seconds")
                    
                    # process the new file
                    self.process_new_file(new_file)
                    return True
                else:
                    logger.info("no new files - data is up to date")
                    return False
            else:
                logger.warning("could not download files from bls")
                return False
                
        except Exception as e:
            logger.error(f"error checking for files: {e}")
            return False
        finally:
            self.last_check = datetime.now()
    
    def get_current_files(self):
        """Get a list of current Excel files"""
        try:
            files = list(Config.DATA_SHEET_DIR.glob(Config.EXCEL_FILE_PATTERN))
            return sorted(files, key=lambda f: f.stat().st_mtime, reverse=True)
        except Exception as e:
            logger.error(f"error getting current files: {e}")
            return []
    
    def process_new_file(self, excel_file):
        """Process a newly downloaded Excel file"""
        logger.info(f"processing {excel_file.name}")
        start_time = time.time()
        
        try:
            # extract data from the excel file
            data = self.processor.extract_cpi_data(excel_file)
            
            if data:
                process_time = time.time() - start_time
                logger.info(f"processed {len(data)} data points")
                logger.info(f"processing took {process_time:.2f} seconds")
                
                # show some sample data
                self.show_sample_data(data)
            else:
                logger.warning("no data extracted from file")
                
        except Exception as e:
            logger.error(f"error processing file: {e}")
    
    def show_sample_data(self, data):
        """Show a sample of the data we extracted"""
        if not data:
            return
            
        logger.info("sample of extracted data:")
        
        # show first few data points
        for i, item in enumerate(data[:3]):
            if 'ticker' in item and 'value' in item:
                ticker = item.get('ticker', 'Unknown')
                value = item.get('value', 'N/A')
                year = item.get('year', 'N/A')
                month = item.get('month', 'N/A')
                logger.info(f"   {ticker}: {value} ({year}-{month:02d})")
        
        if len(data) > 3:
            logger.info(f"   and {len(data) - 3} more data points")
    
    def get_latest_data(self, category="cpi"):
        """Get the latest data for a category"""
        try:
            # find the most recent excel file
            files = self.get_current_files()
            if not files:
                logger.warning("no excel files found")
                return None
            
            latest_file = files[0]  # already sorted by most recent
            logger.info(f"getting data from: {latest_file.name}")
            
            # extract data
            data = self.processor.extract_cpi_data(latest_file, category)
            
            if data:
                logger.info(f"found {len(data)} data points for {category}")
                return data
            else:
                logger.warning(f"no data found for {category}")
                return None
                
        except Exception as e:
            logger.error(f"error getting latest data: {e}")
            return None
    
    def print_status(self):
        """Print current status"""
        print("\n" + "="*50)
        print("bls scraper status")
        print("="*50)
        
        # basic info
        files = self.get_current_files()
        print(f"excel files: {len(files)}")
        print(f"files downloaded this session: {self.files_downloaded}")
        
        # timing info
        if self.last_check:
            print(f"last check: {self.last_check.strftime('%H:%M:%S')}")
        
        if self.last_download:
            print(f"last download: {self.last_download.strftime('%H:%M:%S')}")
        
        # show latest file
        if files:
            latest = files[0]
            file_time = datetime.fromtimestamp(latest.stat().st_mtime)
            print(f"latest file: {latest.name} ({file_time.strftime('%H:%M:%S')})")
        
        print("="*50)
    
    def run_continuous(self):
        """Run the scraper continuously"""
        logger.info("starting continuous mode")
        logger.info("press ctrl+c to stop")
        
        try:
            while True:
                self.check_for_new_files()
                self.print_status()
                
                # wait 30 minutes before checking again
                logger.info("waiting 30 minutes before next check")
                time.sleep(30 * 60)
                
        except KeyboardInterrupt:
            logger.info("stopping scraper")
        except Exception as e:
            logger.error(f"unexpected error: {e}")
    
    def run_once(self):
        """Run the scraper once and exit"""
        logger.info("running one-time check")
        
        success = self.check_for_new_files()
        self.print_status()
        
        if success:
            logger.info("successfully downloaded and processed new data")
        else:
            logger.info("no new data available")
        
        return success


def get_cpi_data():
    """Function to get CPI data"""
    logger.info("getting latest cpi data")
    
    scraper = BLSScraper()
    
    # first check for new files
    scraper.check_for_new_files()
    
    # get the data
    data = scraper.get_latest_data("cpi")
    
    if data:
        # convert to a simple pandas dataframe
        df = pd.DataFrame(data)
        logger.info(f"retrieved {len(df)} cpi data points")
        return df
    else:
        logger.warning("no cpi data available")
        return pd.DataFrame()


def main():
    """Main function - choose what to do"""
    import sys
    
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
    else:
        mode = "once"
    
    scraper = BLSScraper()
    
    if mode == "continuous" or mode == "watch":
        scraper.run_continuous()
    elif mode == "data":
        data = get_cpi_data()
        if not data.empty:
            print(data.head())
    else:
        scraper.run_once()


if __name__ == "__main__":
    main()