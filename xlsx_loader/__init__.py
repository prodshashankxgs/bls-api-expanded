#!/usr/bin/env python3
"""
BLS Excel Data Loader
====================

Excel-based data loading system for BLS CPI supplemental files.
Provides interface for downloading and processing Excel files from BLS.

Usage:
    from xlsx_loader import ExcelDataLoader
    
    loader = ExcelDataLoader()
    data = loader.load_data("cpi", "2025-06")
"""

from .downloader import BLSExcelDownloader
from .processor import ExcelDataProcessor

__version__ = "1.0.0"
__all__ = ["ExcelDataLoader", "BLSExcelDownloader", "ExcelDataProcessor"]


class ExcelDataLoader:
    """
    Main interface for Excel-based BLS data loading
    """
    
    def __init__(self, data_sheet_dir: str = "data_sheet"):
        """
        Initialize Excel data loader
        
        Args:
            data_sheet_dir: Directory to store Excel files
        """
        self.downloader = BLSExcelDownloader(data_sheet_dir)
        self.processor = ExcelDataProcessor(data_sheet_dir)
    
    def load_data(self, ticker: str, date: str = None) -> list:
        """
        Load CPI data from Excel files
        
        Args:
            ticker: Data type (e.g., 'cpi', 'cpi_u')
            date: Date specification (e.g., '2025-06')
            
        Returns:
            List of data dictionaries compatible with existing data_loader
        """
        # Download the latest Excel file if needed
        excel_file = self.downloader.download_latest_cpi_file(date)
        
        if not excel_file:
            return []
        
        # Process the Excel file and return data
        return self.processor.extract_cpi_data(excel_file, ticker, date)
    
    def get_available_files(self) -> list:
        """Get list of available Excel files"""
        return self.downloader.get_available_files()
    
    def cleanup_old_files(self, keep_days: int = 30):
        """Remove old Excel files"""
        self.downloader.cleanup_old_files(keep_days)