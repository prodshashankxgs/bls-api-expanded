#!/usr/bin/env python3
"""
BLS Excel File Downloader
=========================

Downloads CPI supplemental Excel files from BLS website.
Handles navigation to https://www.bls.gov/cpi/tables/supplemental-files/
and automatic detection of CPI-U Excel files.
"""

import os
import re
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# Import configuration
sys_path = str(Path(__file__).parent.parent)
if sys_path not in os.sys.path:
    os.sys.path.insert(0, sys_path)
from config import Config

logger = logging.getLogger(__name__)


class BLSExcelDownloader:
    """
    Downloads Excel files from BLS supplemental files page
    """
    
    def __init__(self, data_sheet_dir: str = None):
        """
        Initialize downloader
        
        Args:
            data_sheet_dir: Directory to save Excel files (defaults to config setting)
        """
        if data_sheet_dir is None:
            self.data_sheet_dir = Config.DATA_SHEET_DIR
        else:
            self.data_sheet_dir = Path(data_sheet_dir)
        
        self.data_sheet_dir.mkdir(exist_ok=True)
        
        self.base_url = Config.BLS_CPI_SUPPLEMENTAL_URL
        self.session = self._create_session()
        
    def _create_session(self) -> requests.Session:
        """Create optimized requests session"""
        session = requests.Session()
        
        retry_strategy = Retry(
            total=Config.MAX_RETRIES,
            backoff_factor=Config.RETRY_BACKOFF_FACTOR,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
        })
        
        return session
        
    def get_supplemental_files_page(self) -> Optional[BeautifulSoup]:
        """
        Fetch and parse the BLS supplemental files page
        
        Returns:
            BeautifulSoup object of the page or None if failed
        """
        try:
            logger.info(f"fetching bls supplemental files page: {self.base_url}")
            
            response = self.session.get(self.base_url, timeout=Config.HTTP_TIMEOUT)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            logger.info("successfully fetched bls supplemental files page")
            
            return soup
            
        except requests.RequestException as e:
            logger.error(f"failed to fetch bls page: {e}")
            return None
        except Exception as e:
            logger.error(f"unexpected error fetching bls page: {e}")
            return None
    
    def find_cpi_excel_links(self, soup: BeautifulSoup, target_date: str = None) -> List[Dict]:
        """
        Find CPI-U Excel file links on the page
        
        Args:
            soup: BeautifulSoup object of the page
            target_date: Target date like '2025-06' or 'June 2025'
            
        Returns:
            List of dicts with file info: {'url', 'filename', 'date', 'description'}
        """
        excel_links = []
        
        try:
            # Look for links to Excel files (.xlsx, .xls)
            excel_pattern = re.compile(r'\.xlsx?$', re.IGNORECASE)
            
            # Prioritize files with cpi-u-YYYYMM.xlsx pattern
            cpi_u_pattern = re.compile(r'cpi-u-\d{6}\.xlsx$', re.IGNORECASE)
            # Look for exact "CPI-U" text in link text
            cpi_u_text_pattern = re.compile(r'^CPI-U$', re.IGNORECASE)
            # Fallback to general CPI-U pattern
            cpi_pattern = re.compile(r'cpi.*u', re.IGNORECASE)
            
            # Find all links
            links = soup.find_all('a', href=True)
            
            for link in links:
                href = link.get('href', '')
                text = link.get_text(strip=True)
                
                # Check if it's an Excel file
                if excel_pattern.search(href):
                    # Check if it matches the specific cpi-u-YYYYMM.xlsx pattern first
                    is_cpi_u_file = cpi_u_pattern.search(href) or cpi_u_pattern.search(text)
                    # Check for exact "CPI-U" text
                    is_cpi_u_text = cpi_u_text_pattern.match(text.strip())
                    # Fallback to general CPI-U pattern
                    is_cpi_general = cpi_pattern.search(text) or cpi_pattern.search(href)
                    
                    if is_cpi_u_file or is_cpi_general:
                        
                        # Build full URL
                        if href.startswith('http'):
                            full_url = href
                        else:
                            full_url = urljoin(self.base_url, href)
                        
                        # Extract filename
                        filename = os.path.basename(urlparse(full_url).path)
                        
                        # Try to extract date from text or filename
                        date_info = self._extract_date_from_text(text + ' ' + filename)
                        
                        # Prioritize cpi-u-YYYYMM.xlsx files
                        priority = 1 if is_cpi_u_file else 2
                        
                        excel_links.append({
                            'url': full_url,
                            'filename': filename,
                            'date': date_info,
                            'description': text,
                            'link_text': text,
                            'priority': priority
                        })
            
            # Sort by priority first (cpi-u-YYYYMM.xlsx files first), then by date (most recent first)
            excel_links.sort(key=lambda x: (x.get('priority', 2), -int(x.get('date', '').replace('-', '') or '0')))
            
            logger.info(f"found {len(excel_links)} cpi excel files")
            for link in excel_links[:5]:  # Log first 5
                logger.info(f"- {link['filename']}: {link['description']}")
                
            return excel_links
            
        except Exception as e:
            logger.error(f"error finding excel links: {e}")
            return []
    
    def _extract_date_from_text(self, text: str) -> str:
        """
        Extract date from text (filename or description)
        
        Args:
            text: Text to search for date
            
        Returns:
            Date string in YYYY-MM format or empty string
        """
        try:
            text = text.lower()
            
            # Month mapping
            months = {
                'january': '01', 'jan': '01',
                'february': '02', 'feb': '02',
                'march': '03', 'mar': '03',
                'april': '04', 'apr': '04',
                'may': '05',
                'june': '06', 'jun': '06',
                'july': '07', 'jul': '07',
                'august': '08', 'aug': '08',
                'september': '09', 'sep': '09', 'sept': '09',
                'october': '10', 'oct': '10',
                'november': '11', 'nov': '11',
                'december': '12', 'dec': '12'
            }
            
            # Look for patterns like "June 2025", "2025-06", etc.
            patterns = [
                r'(\w+)\s+(\d{4})',  # "June 2025"
                r'(\d{4})-(\d{2})',   # "2025-06"
                r'(\d{4})(\d{2})',    # "202506"
            ]
            
            for pattern in patterns:
                match = re.search(pattern, text)
                if match:
                    if pattern == patterns[0]:  # Month Year format
                        month_name = match.group(1)
                        year = match.group(2)
                        month_num = months.get(month_name, '')
                        if month_num:
                            return f"{year}-{month_num}"
                    elif pattern == patterns[1]:  # YYYY-MM format
                        return f"{match.group(1)}-{match.group(2)}"
                    elif pattern == patterns[2]:  # YYYYMM format
                        year = match.group(1)
                        month = match.group(2)
                        return f"{year}-{month}"
            
            # Default to current date if no date found
            return datetime.now().strftime("%Y-%m")
            
        except Exception as e:
            logger.debug(f"error extracting date from '{text}': {e}")
            return ""
    
    def download_file(self, url: str, filename: str) -> Optional[Path]:
        """
        Download a file from URL
        
        Args:
            url: File URL
            filename: Local filename to save as
            
        Returns:
            Path to downloaded file or None if failed
        """
        try:
            file_path = self.data_sheet_dir / filename
            
            # Skip if file already exists and is recent
            if file_path.exists():
                file_age = datetime.now() - datetime.fromtimestamp(file_path.stat().st_mtime)
                if file_age < timedelta(hours=Config.EXCEL_FILE_MAX_AGE_HOURS):
                    logger.info(f"file {filename} already exists and is recent")
                    return file_path
            
            logger.info(f"downloading {filename} from {url}")
            
            response = self.session.get(url, timeout=Config.DOWNLOAD_TIMEOUT, stream=True, verify=False)
            response.raise_for_status()
            
            # check content type
            content_type = response.headers.get('content-type', '').lower()
            if 'excel' not in content_type and 'spreadsheet' not in content_type and 'octet-stream' not in content_type:
                logger.warning(f"unexpected content type: {content_type}")
            
            # download file
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            logger.info(f"successfully downloaded {filename} ({file_path.stat().st_size} bytes)")
            return file_path
            
        except requests.RequestException as e:
            logger.error(f"failed to download {filename}: {e}")
            return None
        except Exception as e:
            logger.error(f"unexpected error downloading {filename}: {e}")
            return None
    
    def download_latest_cpi_file(self, target_date: str = None) -> Optional[Path]:
        """
        Download the latest or target CPI-U Excel file
        
        Args:
            target_date: Target date like '2025-06' or None for latest
            
        Returns:
            Path to downloaded file or None if failed
        """
        try:
            # Get the supplemental files page
            soup = self.get_supplemental_files_page()
            if not soup:
                return None
            
            # Find Excel links
            excel_links = self.find_cpi_excel_links(soup, target_date)
            if not excel_links:
                logger.error("no cpi excel files found on bls page")
                return None
            
            # Find target file
            target_file = None
            
            if target_date:
                # Convert target_date to YYYYMM format for filename matching
                target_yyyymm = target_date.replace('-', '')
                target_filename = f"cpi-u-{target_yyyymm}.xlsx"
                
                # Look for specific cpi-u-YYYYMM.xlsx file first
                for link in excel_links:
                    if target_filename.lower() in link.get('filename', '').lower():
                        target_file = link
                        logger.info(f"found target file: {target_file['filename']}")
                        break
                
                # Fallback to date matching in filename or date field
                if not target_file:
                    for link in excel_links:
                        if target_date in link.get('date', '') or target_yyyymm in link.get('filename', ''):
                            target_file = link
                            break
            
            # If no specific target found, use the highest priority (cpi-u-YYYYMM.xlsx) file
            if not target_file:
                target_file = excel_links[0]
                logger.info(f"using most recent file: {target_file['filename']}")
            
            # Download the file
            return self.download_file(target_file['url'], target_file['filename'])
            
        except Exception as e:
            logger.error(f"error downloading cpi file: {e}")
            return None
    
    def get_available_files(self) -> List[str]:
        """Get list of downloaded Excel files"""
        try:
            files = []
            for file_path in self.data_sheet_dir.glob(Config.EXCEL_FILE_PATTERN):
                files.append(file_path.name)
            return sorted(files, reverse=True)  # Most recent first
        except Exception as e:
            logger.error(f"error listing files: {e}")
            return []
    
    def cleanup_old_files(self, keep_days: int = 30):
        """Remove Excel files older than specified days"""
        try:
            cutoff_time = datetime.now() - timedelta(days=keep_days)
            
            for file_path in self.data_sheet_dir.glob(Config.EXCEL_FILE_PATTERN):
                if datetime.fromtimestamp(file_path.stat().st_mtime) < cutoff_time:
                    file_path.unlink()
                    logger.info(f"removed old file: {file_path.name}")
                    
        except Exception as e:
            logger.error(f"error cleaning up files: {e}")


if __name__ == "__main__":
    # Test the downloader
    logging.basicConfig(level=logging.INFO)
    
    downloader = BLSExcelDownloader()
    file_path = downloader.download_latest_cpi_file("2025-06")
    
    if file_path:
        print(f"Successfully downloaded: {file_path}")
    else:
        print("Download failed")