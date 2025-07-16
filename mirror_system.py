"""
Website Mirroring System for FRED Scraper
Provides intelligent caching and rotation to avoid captcha/detection
"""

import os
import hashlib
import time
import json
import gzip
import pickle
from datetime import datetime, timedelta
from typing import Dict, Optional, Any, List
from urllib.parse import urlparse, urljoin
import logging
from dataclasses import dataclass, asdict


@dataclass
class MirrorEntry:
    """Represents a cached page in the mirror system"""
    url: str
    content: bytes
    headers: Dict[str, str]
    status_code: int
    timestamp: datetime
    content_type: str
    encoding: str = 'utf-8'
    compressed: bool = False
    access_count: int = 0
    last_accessed: Optional[datetime] = None


class MirrorCache:
    """Intelligent caching system for web pages"""
    
    def __init__(self, 
                 cache_dir: str = "mirrors",
                 max_age_hours: int = 24,
                 max_size_mb: int = 500,
                 compress: bool = True):
        
        self.cache_dir = cache_dir
        self.max_age = timedelta(hours=max_age_hours)
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.compress = compress
        self.logger = logging.getLogger(__name__)
        
        # Create cache directory structure
        os.makedirs(cache_dir, exist_ok=True)
        os.makedirs(os.path.join(cache_dir, 'pages'), exist_ok=True)
        os.makedirs(os.path.join(cache_dir, 'metadata'), exist_ok=True)
        
        # Load existing cache index
        self.index_file = os.path.join(cache_dir, 'cache_index.json')
        self.cache_index = self._load_cache_index()
    
    def _load_cache_index(self) -> Dict[str, Dict]:
        """Load cache index from disk"""
        try:
            if os.path.exists(self.index_file):
                with open(self.index_file, 'r') as f:
                    index_data = json.load(f)
                
                # Convert timestamp strings back to datetime objects
                for url_hash, entry_data in index_data.items():
                    if 'timestamp' in entry_data:
                        entry_data['timestamp'] = datetime.fromisoformat(entry_data['timestamp'])
                    if 'last_accessed' in entry_data and entry_data['last_accessed']:
                        entry_data['last_accessed'] = datetime.fromisoformat(entry_data['last_accessed'])
                
                return index_data
        except Exception as e:
            self.logger.error(f"Error loading cache index: {e}")
        
        return {}
    
    def _save_cache_index(self):
        """Save cache index to disk"""
        try:
            # Convert datetime objects to strings for JSON serialization
            serializable_index = {}
            for url_hash, entry_data in self.cache_index.items():
                serializable_entry = entry_data.copy()
                if 'timestamp' in serializable_entry:
                    serializable_entry['timestamp'] = serializable_entry['timestamp'].isoformat()
                if 'last_accessed' in serializable_entry and serializable_entry['last_accessed']:
                    serializable_entry['last_accessed'] = serializable_entry['last_accessed'].isoformat()
                serializable_index[url_hash] = serializable_entry
            
            with open(self.index_file, 'w') as f:
                json.dump(serializable_index, f, indent=2)
        
        except Exception as e:
            self.logger.error(f"Error saving cache index: {e}")
    
    def _get_url_hash(self, url: str) -> str:
        """Get consistent hash for URL"""
        return hashlib.md5(url.encode()).hexdigest()
    
    def _get_cache_path(self, url_hash: str) -> str:
        """Get file path for cached content"""
        return os.path.join(self.cache_dir, 'pages', f"{url_hash}.cache")
    
    def _get_metadata_path(self, url_hash: str) -> str:
        """Get file path for cached metadata"""
        return os.path.join(self.cache_dir, 'metadata', f"{url_hash}.meta")
    
    def is_cached(self, url: str) -> bool:
        """Check if URL is cached and still valid"""
        url_hash = self._get_url_hash(url)
        
        if url_hash not in self.cache_index:
            return False
        
        entry_data = self.cache_index[url_hash]
        timestamp = entry_data.get('timestamp')
        
        if not timestamp:
            return False
        
        # Check if cache is expired
        if datetime.now() - timestamp > self.max_age:
            self._remove_from_cache(url_hash)
            return False
        
        # Check if file exists
        cache_path = self._get_cache_path(url_hash)
        if not os.path.exists(cache_path):
            self._remove_from_cache(url_hash)
            return False
        
        return True
    
    def get_cached(self, url: str) -> Optional[MirrorEntry]:
        """Retrieve cached content for URL"""
        if not self.is_cached(url):
            return None
        
        url_hash = self._get_url_hash(url)
        
        try:
            # Load content
            cache_path = self._get_cache_path(url_hash)
            
            with open(cache_path, 'rb') as f:
                content = f.read()
            
            # Decompress if needed
            entry_data = self.cache_index[url_hash]
            if entry_data.get('compressed', False):
                content = gzip.decompress(content)
            
            # Update access statistics
            entry_data['access_count'] = entry_data.get('access_count', 0) + 1
            entry_data['last_accessed'] = datetime.now()
            self.cache_index[url_hash] = entry_data
            
            # Create MirrorEntry object
            mirror_entry = MirrorEntry(
                url=url,
                content=content,
                headers=entry_data.get('headers', {}),
                status_code=entry_data.get('status_code', 200),
                timestamp=entry_data['timestamp'],
                content_type=entry_data.get('content_type', 'text/html'),
                encoding=entry_data.get('encoding', 'utf-8'),
                compressed=entry_data.get('compressed', False),
                access_count=entry_data['access_count'],
                last_accessed=entry_data['last_accessed']
            )
            
            self.logger.debug(f"Cache hit for {url}")
            return mirror_entry
        
        except Exception as e:
            self.logger.error(f"Error retrieving cached content for {url}: {e}")
            self._remove_from_cache(url_hash)
            return None
    
    def store_in_cache(self, 
                      url: str, 
                      content: bytes, 
                      headers: Dict[str, str], 
                      status_code: int = 200) -> bool:
        """Store content in cache"""
        try:
            url_hash = self._get_url_hash(url)
            cache_path = self._get_cache_path(url_hash)
            
            # Compress content if enabled
            final_content = content
            compressed = False
            if self.compress and len(content) > 1024:  # Only compress if > 1KB
                final_content = gzip.compress(content)
                compressed = True
            
            # Store content
            with open(cache_path, 'wb') as f:
                f.write(final_content)
            
            # Update cache index
            content_type = headers.get('content-type', 'text/html')
            encoding = 'utf-8'
            if 'charset=' in content_type:
                encoding = content_type.split('charset=')[1].split(';')[0].strip()
            
            entry_data = {
                'url': url,
                'headers': dict(headers),
                'status_code': status_code,
                'timestamp': datetime.now(),
                'content_type': content_type,
                'encoding': encoding,
                'compressed': compressed,
                'access_count': 0,
                'last_accessed': None,
                'size_bytes': len(final_content)
            }
            
            self.cache_index[url_hash] = entry_data
            self._save_cache_index()
            
            # Clean up cache if it's getting too large
            self._cleanup_cache()
            
            self.logger.debug(f"Cached {url} ({len(content)} bytes)")
            return True
        
        except Exception as e:
            self.logger.error(f"Error storing content in cache for {url}: {e}")
            return False
    
    def _remove_from_cache(self, url_hash: str):
        """Remove entry from cache"""
        try:
            cache_path = self._get_cache_path(url_hash)
            metadata_path = self._get_metadata_path(url_hash)
            
            # Remove files
            if os.path.exists(cache_path):
                os.remove(cache_path)
            if os.path.exists(metadata_path):
                os.remove(metadata_path)
            
            # Remove from index
            if url_hash in self.cache_index:
                del self.cache_index[url_hash]
        
        except Exception as e:
            self.logger.error(f"Error removing cache entry {url_hash}: {e}")
    
    def _cleanup_cache(self):
        """Clean up old cache entries if cache is too large"""
        try:
            # Calculate total cache size
            total_size = sum(
                entry.get('size_bytes', 0) 
                for entry in self.cache_index.values()
            )
            
            if total_size <= self.max_size_bytes:
                return
            
            # Sort entries by last accessed time (LRU)
            entries_by_access = sorted(
                self.cache_index.items(),
                key=lambda x: x[1].get('last_accessed', x[1]['timestamp'])
            )
            
            # Remove oldest entries until under size limit
            for url_hash, entry_data in entries_by_access:
                if total_size <= self.max_size_bytes:
                    break
                
                total_size -= entry_data.get('size_bytes', 0)
                self._remove_from_cache(url_hash)
                self.logger.debug(f"Removed old cache entry for {entry_data['url']}")
            
            self._save_cache_index()
        
        except Exception as e:
            self.logger.error(f"Error during cache cleanup: {e}")
    
    def clear_cache(self):
        """Clear all cached content"""
        try:
            # Remove all cache files
            pages_dir = os.path.join(self.cache_dir, 'pages')
            metadata_dir = os.path.join(self.cache_dir, 'metadata')
            
            for filename in os.listdir(pages_dir):
                os.remove(os.path.join(pages_dir, filename))
            
            for filename in os.listdir(metadata_dir):
                os.remove(os.path.join(metadata_dir, filename))
            
            # Clear index
            self.cache_index = {}
            self._save_cache_index()
            
            self.logger.info("Cache cleared")
        
        except Exception as e:
            self.logger.error(f"Error clearing cache: {e}")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_entries = len(self.cache_index)
        total_size = sum(
            entry.get('size_bytes', 0) 
            for entry in self.cache_index.values()
        )
        
        # Count by domain
        domain_counts = {}
        for entry in self.cache_index.values():
            domain = urlparse(entry['url']).netloc
            domain_counts[domain] = domain_counts.get(domain, 0) + 1
        
        return {
            'total_entries': total_entries,
            'total_size_mb': total_size / (1024 * 1024),
            'max_size_mb': self.max_size_bytes / (1024 * 1024),
            'utilization_percent': (total_size / self.max_size_bytes) * 100,
            'domains': domain_counts,
            'oldest_entry': min(
                (entry['timestamp'] for entry in self.cache_index.values()),
                default=None
            ),
            'newest_entry': max(
                (entry['timestamp'] for entry in self.cache_index.values()),
                default=None
            )
        }


class RotationManager:
    """Manages rotation of user agents, delays, and other stealth measures"""
    
    def __init__(self):
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:122.0) Gecko/20100101 Firefox/122.0',
        ]
        
        self.request_history = []
        self.last_request_time = None
        self.logger = logging.getLogger(__name__)
    
    def get_random_user_agent(self) -> str:
        """Get a random user agent"""
        import random
        return random.choice(self.user_agents)
    
    def get_delay(self, base_delay: float = 2.0) -> float:
        """Get intelligent delay based on request history"""
        import random
        
        # Add randomization to base delay
        delay = base_delay + random.uniform(-0.5, 1.0)
        
        # Increase delay if making frequent requests
        recent_requests = len([
            req for req in self.request_history 
            if datetime.now() - req < timedelta(minutes=1)
        ])
        
        if recent_requests > 10:
            delay *= 2
        elif recent_requests > 5:
            delay *= 1.5
        
        return max(delay, 1.0)  # Minimum 1 second delay
    
    def record_request(self, url: str):
        """Record a request for tracking"""
        self.request_history.append(datetime.now())
        self.last_request_time = datetime.now()
        
        # Clean old history (keep only last hour)
        cutoff = datetime.now() - timedelta(hours=1)
        self.request_history = [
            req for req in self.request_history if req > cutoff
        ]
    
    def should_delay(self) -> bool:
        """Check if we should add extra delay"""
        if not self.last_request_time:
            return False
        
        time_since_last = datetime.now() - self.last_request_time
        return time_since_last < timedelta(seconds=1)


# Global instances
mirror_cache = MirrorCache()
rotation_manager = RotationManager()


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Test the mirror cache
    cache = MirrorCache(cache_dir="test_mirrors")
    
    # Simulate storing content
    test_content = b"<html><body>Test content</body></html>"
    test_headers = {'content-type': 'text/html; charset=utf-8'}
    
    success = cache.store_in_cache(
        "https://fred.stlouisfed.org/series/GDP",
        test_content,
        test_headers
    )
    
    print(f"Storage success: {success}")
    
    # Test retrieval
    if cache.is_cached("https://fred.stlouisfed.org/series/GDP"):
        entry = cache.get_cached("https://fred.stlouisfed.org/series/GDP")
        if entry:
            print(f"Retrieved content: {len(entry.content)} bytes")
            print(f"Content type: {entry.content_type}")
    
    # Print cache stats
    stats = cache.get_cache_stats()
    print(f"Cache stats: {stats}") 