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

logger = logging.getLogger(__name__)


class BLSExcelDownloader:
    """
    Downloads Excel files from BLS supplemental files page
    """
    
    def __init__(self, data_sheet_dir: str = "data_sheet"):
        """
        Initialize downloader
        
        Args:
            data_sheet_dir: Directory to save Excel files
        """
        self.data_sheet_dir = Path(data_sheet_dir)
        self.data_sheet_dir.mkdir(exist_ok=True)
        
        self.base_url = "https://www.bls.gov/cpi/tables/supplemental-files/"
        self.session = self._create_session()
        
    def _create_session(self) -> requests.Session:
        """Create optimized requests session"""
        session = requests.Session()
        
        retry_strategy = Retry(
            total=3,
            backoff_factor=2,
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
            logger.info(f"Fetching BLS supplemental files page: {self.base_url}")
            
            response = self.session.get(self.base_url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            logger.info("Successfully fetched BLS supplemental files page")
            
            return soup
            
        except requests.RequestException as e:
            logger.error(f"Failed to fetch BLS page: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching BLS page: {e}")
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
            cpi_pattern = re.compile(r'cpi.*u', re.IGNORECASE)
            
            # Find all links
            links = soup.find_all('a', href=True)
            
            for link in links:
                href = link.get('href', '')
                text = link.get_text(strip=True)
                
                # Check if it's an Excel file
                if excel_pattern.search(href):
                    # Check if it's CPI-U related
                    if cpi_pattern.search(text) or cpi_pattern.search(href):
                        
                        # Build full URL
                        if href.startswith('http'):
                            full_url = href
                        else:
                            full_url = urljoin(self.base_url, href)
                        
                        # Extract filename
                        filename = os.path.basename(urlparse(full_url).path)
                        
                        # Try to extract date from text or filename
                        date_info = self._extract_date_from_text(text + ' ' + filename)
                        
                        excel_links.append({
                            'url': full_url,
                            'filename': filename,
                            'date': date_info,
                            'description': text,
                            'link_text': text
                        })
            
            # Sort by date (most recent first)
            excel_links.sort(key=lambda x: x.get('date', ''), reverse=True)
            
            logger.info(f"Found {len(excel_links)} CPI Excel files")
            for link in excel_links[:5]:  # Log first 5
                logger.info(f"  - {link['filename']}: {link['description']}")
                
            return excel_links
            
        except Exception as e:
            logger.error(f"Error finding Excel links: {e}")
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
            logger.debug(f"Error extracting date from '{text}': {e}")
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
                if file_age < timedelta(hours=6):  # Skip if less than 6 hours old
                    logger.info(f"File {filename} already exists and is recent")
                    return file_path
            
            logger.info(f"Downloading {filename} from {url}")
            
            response = self.session.get(url, timeout=60, stream=True)
            response.raise_for_status()
            
            # Check content type
            content_type = response.headers.get('content-type', '').lower()
            if 'excel' not in content_type and 'spreadsheet' not in content_type and 'octet-stream' not in content_type:
                logger.warning(f"Unexpected content type: {content_type}")
            
            # Download file
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            logger.info(f"Successfully downloaded {filename} ({file_path.stat().st_size} bytes)")
            return file_path
            
        except requests.RequestException as e:
            logger.error(f"Failed to download {filename}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error downloading {filename}: {e}")
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
                logger.error("No CPI Excel files found on BLS page")
                return None
            
            # Find target file
            target_file = None
            
            if target_date:
                # Look for specific date
                for link in excel_links:
                    if target_date in link.get('date', '') or target_date.replace('-', '') in link.get('filename', ''):
                        target_file = link
                        break
            
            # If no specific target found, use the most recent
            if not target_file:
                target_file = excel_links[0]
                logger.info(f"Using most recent file: {target_file['filename']}")
            
            # Download the file
            return self.download_file(target_file['url'], target_file['filename'])
            
        except Exception as e:
            logger.error(f"Error downloading CPI file: {e}")
            return None
    
    def get_available_files(self) -> List[str]:
        """Get list of downloaded Excel files"""
        try:
            files = []
            for file_path in self.data_sheet_dir.glob("*.xlsx"):
                files.append(file_path.name)
            return sorted(files, reverse=True)  # Most recent first
        except Exception as e:
            logger.error(f"Error listing files: {e}")
            return []
    
    def cleanup_old_files(self, keep_days: int = 30):
        """Remove Excel files older than specified days"""
        try:
            cutoff_time = datetime.now() - timedelta(days=keep_days)
            
            for file_path in self.data_sheet_dir.glob("*.xlsx"):
                if datetime.fromtimestamp(file_path.stat().st_mtime) < cutoff_time:
                    file_path.unlink()
                    logger.info(f"Removed old file: {file_path.name}")
                    
        except Exception as e:
            logger.error(f"Error cleaning up files: {e}")


if __name__ == "__main__":
    # Test the downloader
    logging.basicConfig(level=logging.INFO)
    
    downloader = BLSExcelDownloader()
    file_path = downloader.download_latest_cpi_file("2025-06")
    
    if file_path:
        print(f"Successfully downloaded: {file_path}")
    else:
        print("Download failed")