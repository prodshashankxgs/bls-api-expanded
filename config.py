# Libraries
import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class Config:
    @staticmethod
    def _get_project_root() -> Path:
        """
        Automatically detect the project root directory.
        Works by finding the directory containing key project files.
        """
        # Start from the current file's directory
        current_dir = Path(__file__).parent.absolute()
        
        # Key files that indicate the project root
        key_files = ['requirements.txt', 'README.md', 'auto_scraper.py', 'bls_api.py']
        
        # Search up the directory tree
        for parent in [current_dir] + list(current_dir.parents):
            if any((parent / key_file).exists() for key_file in key_files):
                return parent
        
        # Fallback to current directory
        logger.warning("could not auto-detect project root, using current directory")
        return current_dir
    
    # Project root (auto-detected)
    PROJECT_ROOT = _get_project_root()

    # Data directories (relative to project root)
    DATA_SHEET_DIR_NAME = os.getenv('BLS_DATA_SHEET_DIR', 'data_sheet')
    CACHE_DIR_NAME = os.getenv('BLS_CACHE_DIR', 'data_cache')
    LOGS_DIR_NAME = os.getenv('BLS_LOGS_DIR', 'logs')
    
    # Full directory paths
    DATA_SHEET_DIR = PROJECT_ROOT / DATA_SHEET_DIR_NAME
    CACHE_DIR = PROJECT_ROOT / CACHE_DIR_NAME
    LOGS_DIR = PROJECT_ROOT / LOGS_DIR_NAME

    # Excel file patterns
    EXCEL_FILE_EXTENSIONS = ['.xlsx', '.xls']
    EXCEL_FILE_PATTERN = '*.xlsx'
    
    # Cache file settings
    CACHE_FILE_EXTENSION = '.json'
    CACHE_PICKLE_EXTENSION = '.pkl'
    
    # Log file settings
    LOG_FILE_NAME = 'bls_scraper.log'
    LOG_FILE_PATH = LOGS_DIR / LOG_FILE_NAME

    # BLS URLs
    BLS_BASE_URL = 'https://www.bls.gov'
    BLS_CPI_SUPPLEMENTAL_URL = 'https://www.bls.gov/cpi/tables/supplemental-files/'
    BLS_API_URL = 'https://api.bls.gov/publicAPI/v2/timeseries/data/'
    
    # Network timeouts
    HTTP_TIMEOUT = int(os.getenv('BLS_HTTP_TIMEOUT', '30'))
    DOWNLOAD_TIMEOUT = int(os.getenv('BLS_DOWNLOAD_TIMEOUT', '300'))  # 5 minutes
    
    # Retry settings
    MAX_RETRIES = int(os.getenv('BLS_MAX_RETRIES', '3'))
    RETRY_BACKOFF_FACTOR = float(os.getenv('BLS_RETRY_BACKOFF', '2.0'))

    # Cache TTL (Time To Live) in seconds
    CACHE_TTL = int(os.getenv('BLS_CACHE_TTL', '3600'))  # 1 hour
    
    # File age settings
    EXCEL_FILE_MAX_AGE_HOURS = int(os.getenv('BLS_EXCEL_MAX_AGE_HOURS', '6'))
    OLD_FILE_CLEANUP_DAYS = int(os.getenv('BLS_OLD_FILE_CLEANUP_DAYS', '30'))
    
    # Threading
    MAX_WORKER_THREADS = int(os.getenv('BLS_MAX_WORKERS', '4'))
    
    # Memory limits
    MAX_CACHE_ENTRIES = int(os.getenv('BLS_MAX_CACHE_ENTRIES', '1000'))
    MAX_RESULTS_PER_REQUEST = int(os.getenv('BLS_MAX_RESULTS', '10000'))
    
    # Server settings
    API_HOST = os.getenv('BLS_API_HOST', '0.0.0.0')
    API_PORT = int(os.getenv('BLS_API_PORT', '8000'))
    API_WORKERS = int(os.getenv('BLS_API_WORKERS', '1'))
    API_RELOAD = os.getenv('BLS_API_RELOAD', 'false').lower() == 'true'
    
    # Log levels
    LOG_LEVEL = os.getenv('BLS_LOG_LEVEL', 'INFO').upper()
    
    # Log format
    LOG_FORMAT = os.getenv('BLS_LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
    
    @classmethod
    def get_excel_file_path(cls, filename: str) -> Path:
        return cls.DATA_SHEET_DIR / filename
    
    @classmethod
    def get_cache_file_path(cls, cache_key: str, extension: str = None) -> Path:
        if extension is None:
            extension = cls.CACHE_FILE_EXTENSION
        
        if not extension.startswith('.'):
            extension = '.' + extension
            
        filename = cache_key + extension
        return cls.CACHE_DIR / filename
    
    @classmethod
    def get_log_file_path(cls, log_name: str = None) -> Path:
        if log_name is None:
            return cls.LOG_FILE_PATH
        
        if not log_name.endswith('.log'):
            log_name += '.log'
            
        return cls.LOGS_DIR / log_name
    
    @classmethod
    def ensure_directories_exist(cls):
        directories = [
            cls.DATA_SHEET_DIR,
            cls.CACHE_DIR,
            cls.LOGS_DIR
        ]
        
        for directory in directories:
            try:
                directory.mkdir(parents=True, exist_ok=True)
                logger.debug(f"ensured directory exists: {directory}")
            except Exception as e:
                logger.error(f"failed to create directory {directory}: {e}")
                raise
    
    @classmethod
    def get_latest_excel_file(cls) -> Optional[Path]:
        try:
            excel_files = list(cls.DATA_SHEET_DIR.glob(cls.EXCEL_FILE_PATTERN))
            if not excel_files:
                return None
            
            # Return the most recently modified file
            latest_file = max(excel_files, key=lambda f: f.stat().st_mtime)
            return latest_file
            
        except Exception as e:
            logger.error(f"error finding latest excel file: {e}")
            return None
    
    @classmethod
    def cleanup_old_files(cls, directory: Path = None, max_age_days: int = None):
        if directory is None:
            directory = cls.CACHE_DIR
        
        if max_age_days is None:
            max_age_days = cls.OLD_FILE_CLEANUP_DAYS
        
        try:
            from datetime import datetime, timedelta
            
            cutoff_time = datetime.now() - timedelta(days=max_age_days)
            cleaned_count = 0
            
            for file_path in directory.iterdir():
                if file_path.is_file():
                    file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if file_mtime < cutoff_time:
                        file_path.unlink()
                        cleaned_count += 1
                        logger.info(f"cleaned up old file: {file_path.name}")
            
            logger.info(f"cleaned up {cleaned_count} old files from {directory}")
            
        except Exception as e:
            logger.error(f"error cleaning up old files: {e}")
    
    @classmethod
    def get_system_info(cls) -> Dict[str, Any]:
        return {
            'platform': sys.platform,
            'python_version': sys.version,
            'project_root': str(cls.PROJECT_ROOT),
            'data_sheet_dir': str(cls.DATA_SHEET_DIR),
            'cache_dir': str(cls.CACHE_DIR),
            'logs_dir': str(cls.LOGS_DIR),
            'directories_exist': {
                'data_sheet': cls.DATA_SHEET_DIR.exists(),
                'cache': cls.CACHE_DIR.exists(),
                'logs': cls.LOGS_DIR.exists()
            },
            'excel_files_count': len(list(cls.DATA_SHEET_DIR.glob(cls.EXCEL_FILE_PATTERN))) if cls.DATA_SHEET_DIR.exists() else 0,
            'environment_variables': {
                'BLS_DATA_SHEET_DIR': os.getenv('BLS_DATA_SHEET_DIR'),
                'BLS_CACHE_DIR': os.getenv('BLS_CACHE_DIR'),
                'BLS_LOG_LEVEL': os.getenv('BLS_LOG_LEVEL'),
            }
        }
    
    @classmethod
    def validate_configuration(cls) -> bool:
        """
        Validate the configuration and environment.
        
        Returns:
            True if configuration is valid, False otherwise
        """
        try:
            # Ensure directories can be created
            cls.ensure_directories_exist()
            
            # Check write permissions
            test_file = cls.CACHE_DIR / 'test_write.tmp'
            test_file.write_text('test')
            test_file.unlink()
            
            logger.info("configuration validation passed")
            return True
            
        except Exception as e:
            logger.error(f"configuration validation failed: {e}")
            return False
    
    @classmethod
    def print_configuration(cls):
        """
        Print current configuration for debugging.
        """
        print("BLS Scraper API Configuration")
        print("=" * 40)
        print(f"Project Root: {cls.PROJECT_ROOT}")
        print(f"Data Directory: {cls.DATA_SHEET_DIR}")
        print(f"Cache Directory: {cls.CACHE_DIR}")
        print(f"Logs Directory: {cls.LOGS_DIR}")
        print(f"Platform: {sys.platform}")
        print(f"Cache TTL: {cls.CACHE_TTL}s")
        print(f"HTTP Timeout: {cls.HTTP_TIMEOUT}s")
        print(f"Log Level: {cls.LOG_LEVEL}")
        print("=" * 40)


# ================================
# INITIALIZATION AND VALIDATION
# ================================

def initialize_config():
    """
    Initialize configuration and create required directories.
    Call this at application startup.
    """
    try:
        # Ensure directories exist
        Config.ensure_directories_exist()
        
        # Validate configuration
        if not Config.validate_configuration():
            logger.warning("configuration validation failed, but continuing...")
        
        logger.info(f"bls scraper api initialized - project root: {Config.PROJECT_ROOT}")
        logger.info(f"data directory: {Config.DATA_SHEET_DIR}")
        logger.info(f"cache directory: {Config.CACHE_DIR}")
        
    except Exception as e:
        logger.error(f"failed to initialize configuration: {e}")
        raise


# Auto-initialize when module is imported
if __name__ != "__main__":
    initialize_config()

if __name__ == "__main__":
    # Test the configuration
    print("Testing BLS Scraper API Configuration...")
    
    # Print configuration
    Config.print_configuration()
    
    # Print system info
    print("\nSystem Information:")
    print("-" * 30)
    system_info = Config.get_system_info()
    for key, value in system_info.items():
        print(f"{key}: {value}")
    
    # Test directory creation
    print(f"\nTesting directory creation...")
    Config.ensure_directories_exist()
    
    # Test file path methods
    print(f"\nTesting path methods...")
    excel_path = Config.get_excel_file_path("test.xlsx")
    cache_path = Config.get_cache_file_path("test_cache")
    log_path = Config.get_log_file_path("test")
    
    print(f"Excel path: {excel_path}")
    print(f"Cache path: {cache_path}")
    print(f"Log path: {log_path}")
    
    # Validate configuration
    print(f"\nValidating configuration...")
    is_valid = Config.validate_configuration()
    print(f"Configuration valid: {is_valid}")
    
    print("Configuration test completed!")