import random
import logging
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware
from scrapy import signals
from scrapy.exceptions import NotConfigured


class UserAgentRotationMiddleware(UserAgentMiddleware):
    """Middleware to rotate user agents for stealth scraping"""
    
    def __init__(self, user_agents):
        super().__init__()
        self.user_agents = user_agents
        
    @classmethod
    def from_crawler(cls, crawler):
        user_agents = crawler.settings.get('USER_AGENTS')
        if not user_agents:
            raise NotConfigured('USER_AGENTS setting is required')
        return cls(user_agents)
    
    def process_request(self, request, spider):
        user_agent = random.choice(self.user_agents)
        request.headers['User-Agent'] = user_agent
        return None


class ProxyRotationMiddleware:
    """Middleware for proxy rotation (optional)"""
    
    def __init__(self, proxies=None):
        self.proxies = proxies or []
        
    @classmethod
    def from_crawler(cls, crawler):
        proxies = crawler.settings.get('PROXY_LIST', [])
        return cls(proxies)
    
    def process_request(self, request, spider):
        if self.proxies:
            proxy = random.choice(self.proxies)
            request.meta['proxy'] = proxy
        return None


class MirrorCacheMiddleware:
    """Middleware to cache pages as mirrors to avoid repeated requests"""
    
    def __init__(self, cache_dir, cache_expiry):
        self.cache_dir = cache_dir
        self.cache_expiry = cache_expiry
        self.logger = logging.getLogger(__name__)
        
    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        cache_dir = settings.get('MIRROR_CACHE_DIR', 'mirrors')
        cache_expiry = settings.get('MIRROR_CACHE_EXPIRY', 3600)
        
        if not settings.getbool('MIRROR_ENABLED', False):
            raise NotConfigured('Mirroring is disabled')
            
        return cls(cache_dir, cache_expiry)
    
    def process_request(self, request, spider):
        # Check if we have a cached version
        # Implementation would check filesystem cache
        return None
    
    def process_response(self, request, response, spider):
        # Save response to cache
        # Implementation would save to filesystem
        return response


class StealthMiddleware:
    """Additional stealth measures"""
    
    def process_request(self, request, spider):
        # Add random delays and other stealth measures
        request.headers.setdefault('Referer', 'https://www.google.com/')
        
        # Simulate real browser behavior
        request.headers.setdefault('DNT', '1')
        request.headers.setdefault('Connection', 'keep-alive')
        
        return None 