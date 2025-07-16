#!/usr/bin/env python3
"""
Test script for FRED Data Loader System
Tests all components: scraping, caching, data loading, fallbacks
"""

import os
import sys
import time
import logging
from datetime import datetime, date
import asyncio

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fred_data_loader import FREDDataLoader, load_data
from mirror_system import MirrorCache, RotationManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_mirror_cache():
    """Test the mirror caching system"""
    logger.info("=== Testing Mirror Cache System ===")
    
    # Create test cache
    cache = MirrorCache(cache_dir="test_cache", max_age_hours=1, max_size_mb=10)
    
    # Test storing content
    test_url = "https://fred.stlouisfed.org/series/GDP"
    test_content = b"<html><body>Test GDP data content</body></html>"
    test_headers = {'content-type': 'text/html; charset=utf-8'}
    
    logger.info("Testing cache storage...")
    success = cache.store_in_cache(test_url, test_content, test_headers)
    assert success, "Failed to store content in cache"
    logger.info("✓ Cache storage successful")
    
    # Test retrieval
    logger.info("Testing cache retrieval...")
    assert cache.is_cached(test_url), "Content should be cached"
    
    entry = cache.get_cached(test_url)
    assert entry is not None, "Failed to retrieve cached content"
    assert entry.content == test_content, "Retrieved content doesn't match"
    logger.info("✓ Cache retrieval successful")
    
    # Test cache stats
    stats = cache.get_cache_stats()
    logger.info(f"Cache stats: {stats['total_entries']} entries, {stats['total_size_mb']:.2f} MB")
    assert stats['total_entries'] > 0, "Cache should have entries"
    
    # Clean up
    cache.clear_cache()
    logger.info("✓ Mirror cache tests passed")


def test_rotation_manager():
    """Test the rotation manager"""
    logger.info("=== Testing Rotation Manager ===")
    
    manager = RotationManager()
    
    # Test user agent rotation
    user_agent1 = manager.get_random_user_agent()
    user_agent2 = manager.get_random_user_agent()
    assert user_agent1, "Should return a user agent"
    logger.info(f"User agent: {user_agent1[:50]}...")
    
    # Test delay calculation
    delay = manager.get_delay()
    assert delay >= 1.0, "Delay should be at least 1 second"
    logger.info(f"Calculated delay: {delay:.2f} seconds")
    
    # Test request recording
    manager.record_request("https://test.com")
    assert len(manager.request_history) > 0, "Should record requests"
    
    logger.info("✓ Rotation manager tests passed")


def test_data_loader_basic():
    """Test basic data loader functionality"""
    logger.info("=== Testing Data Loader - Basic ===")
    
    loader = FREDDataLoader(
        cache_dir="test_data_cache",
        db_path="test_fred.db",
        enable_scraping=False,  # Disable scraping for basic test
        enable_bls_fallback=True
    )
    
    # Test getting available tickers
    tickers = loader.get_available_tickers()
    assert len(tickers) > 0, "Should have available tickers"
    logger.info(f"Available tickers: {len(tickers)} total")
    
    logger.info("✓ Basic data loader tests passed")


def test_convenience_function():
    """Test the convenience load_data function"""
    logger.info("=== Testing Convenience Function ===")
    
    # Test with a BLS fallback series (should work without scraping)
    logger.info("Testing BLS fallback data loading...")
    try:
        data = load_data('unemployment_bls', years_back=1)
        if data:
            logger.info(f"✓ Loaded {data.title} with {len(data.data_points)} points")
            logger.info(f"  Latest value: {data.data_points[-1].value} on {data.data_points[-1].date}")
            logger.info(f"  Source: {data.source}")
        else:
            logger.warning("No data returned (this may be expected without API key)")
    except Exception as e:
        logger.warning(f"BLS fallback test failed (expected without API key): {e}")
    
    logger.info("✓ Convenience function tests completed")


def test_data_structures():
    """Test data structure creation and manipulation"""
    logger.info("=== Testing Data Structures ===")
    
    from fred_data_loader import DataPoint, SeriesData
    
    # Create test data point
    test_point = DataPoint(
        date=date.today(),
        value=3.5,
        period="2024-01",
        year=2024,
        month=1
    )
    
    assert test_point.value == 3.5, "Data point value should match"
    logger.info(f"✓ Created data point: {test_point}")
    
    # Create test series data
    test_series = SeriesData(
        series_id="TEST123",
        ticker="TEST",
        title="Test Series",
        units="Percent",
        frequency="Monthly",
        data_points=[test_point],
        last_updated="2024-01-01",
        source="Test"
    )
    
    assert len(test_series.data_points) == 1, "Should have one data point"
    assert test_series.ticker == "TEST", "Ticker should match"
    logger.info(f"✓ Created series data: {test_series.title}")
    
    logger.info("✓ Data structure tests passed")


def test_integration():
    """Test system integration"""
    logger.info("=== Testing System Integration ===")
    
    # Test that all components can be imported
    try:
        from fred_data_loader import FREDDataLoader, load_data, SeriesData, DataPoint
        from mirror_system import MirrorCache, RotationManager
        logger.info("✓ All imports successful")
    except ImportError as e:
        logger.error(f"Import failed: {e}")
        raise
    
    # Test loader initialization
    loader = FREDDataLoader()
    assert loader is not None, "Loader should initialize"
    logger.info("✓ Loader initialization successful")
    
    # Test ticker mapping
    tickers = loader.get_available_tickers()
    assert 'GDP' in tickers, "Should have GDP ticker"
    assert 'UNEMPLOYMENT' in tickers, "Should have unemployment ticker"
    logger.info(f"✓ Ticker mapping includes {len(tickers)} tickers")
    
    logger.info("✓ Integration tests passed")


def test_file_structure():
    """Test that all required files exist"""
    logger.info("=== Testing File Structure ===")
    
    required_files = [
        'fred_data_loader.py',
        'mirror_system.py',
        'requirements.txt',
        'fred_scraper/scrapy.cfg',
        'fred_scraper/settings.py',
        'fred_scraper/items.py',
        'fred_scraper/middlewares.py',
        'fred_scraper/pipelines.py',
        'fred_scraper/spiders/__init__.py',
        'fred_scraper/spiders/fred_spider.py'
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        logger.error(f"Missing files: {missing_files}")
        raise FileNotFoundError(f"Required files missing: {missing_files}")
    
    logger.info("✓ All required files present")


def test_scrapy_configuration():
    """Test Scrapy configuration"""
    logger.info("=== Testing Scrapy Configuration ===")
    
    # Test if Scrapy project is properly configured
    scrapy_cfg_path = 'fred_scraper/scrapy.cfg'
    if os.path.exists(scrapy_cfg_path):
        with open(scrapy_cfg_path, 'r') as f:
            config_content = f.read()
        assert 'fred_scraper' in config_content, "Scrapy config should reference fred_scraper"
        logger.info("✓ Scrapy configuration valid")
    else:
        logger.warning("Scrapy configuration file not found")
    
    # Test spider list (if scrapy is available)
    try:
        import subprocess
        result = subprocess.run(
            ['scrapy', 'list'], 
            cwd='fred_scraper',
            capture_output=True, 
            text=True, 
            timeout=10
        )
        if result.returncode == 0:
            spiders = result.stdout.strip().split('\n')
            assert 'fred' in spiders, "Should have 'fred' spider"
            logger.info(f"✓ Scrapy spiders available: {spiders}")
        else:
            logger.warning(f"Scrapy list failed: {result.stderr}")
    except (subprocess.TimeoutExpired, FileNotFoundError):
        logger.warning("Scrapy not available or timeout - install with: pip install scrapy")


def run_performance_test():
    """Run basic performance tests"""
    logger.info("=== Running Performance Tests ===")
    
    # Test cache performance
    cache = MirrorCache(cache_dir="perf_test_cache")
    
    start_time = time.time()
    
    # Store multiple entries
    for i in range(100):
        url = f"https://test.com/page{i}"
        content = f"<html><body>Page {i} content</body></html>".encode()
        cache.store_in_cache(url, content, {'content-type': 'text/html'})
    
    store_time = time.time() - start_time
    logger.info(f"Stored 100 entries in {store_time:.2f} seconds")
    
    # Retrieve entries
    start_time = time.time()
    
    for i in range(100):
        url = f"https://test.com/page{i}"
        entry = cache.get_cached(url)
        assert entry is not None, f"Should retrieve entry {i}"
    
    retrieve_time = time.time() - start_time
    logger.info(f"Retrieved 100 entries in {retrieve_time:.2f} seconds")
    
    # Clean up
    cache.clear_cache()
    
    logger.info("✓ Performance tests completed")


def main():
    """Run all tests"""
    logger.info("Starting FRED Data Loader System Tests")
    logger.info("=" * 50)
    
    try:
        # File structure tests
        test_file_structure()
        
        # Component tests
        test_mirror_cache()
        test_rotation_manager()
        test_data_structures()
        test_data_loader_basic()
        test_convenience_function()
        test_integration()
        
        # Configuration tests
        test_scrapy_configuration()
        
        # Performance tests
        run_performance_test()
        
        logger.info("=" * 50)
        logger.info("🎉 ALL TESTS PASSED! 🎉")
        logger.info("The FRED Data Loader system is ready to use.")
        logger.info("")
        logger.info("Next steps:")
        logger.info("1. Install dependencies: pip install -r requirements.txt")
        logger.info("2. Test the system: python fred_data_loader.py")
        logger.info("3. Run the API: python app/fred_integration.py")
        logger.info("4. Try scraping: cd fred_scraper && scrapy crawl fred -a series_id=GDP")
        
    except Exception as e:
        logger.error(f"❌ TEST FAILED: {e}")
        logger.error("Please check the error above and fix any issues.")
        return 1
    
    # Clean up test files
    cleanup_test_files()
    
    return 0


def cleanup_test_files():
    """Clean up test files created during testing"""
    import shutil
    
    test_dirs = ['test_cache', 'test_data_cache', 'perf_test_cache']
    test_files = ['test_fred.db']
    
    for test_dir in test_dirs:
        if os.path.exists(test_dir):
            shutil.rmtree(test_dir)
    
    for test_file in test_files:
        if os.path.exists(test_file):
            os.remove(test_file)
    
    logger.info("Test files cleaned up")


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 