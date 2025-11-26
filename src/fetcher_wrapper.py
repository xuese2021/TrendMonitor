"""
Enhanced fetcher wrapper with monitoring, caching, and retry logic
"""
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import requests
import logging

logger = logging.getLogger(__name__)

class FetcherWrapper:
    """Wrapper to add retry, caching, and monitoring to fetcher methods"""
    
    def __init__(self, fetcher, config, cache_manager, metrics_tracker):
        self.fetcher = fetcher
        self.config = config
        self.cache = cache_manager
        self.metrics = metrics_tracker
    
    def fetch_with_fallback(self, platform_name, fetch_func):
        """Fetch with cache fallback and metrics tracking"""
        self.metrics.record_platform_attempt(platform_name)
        
        try:
            # Try primary fetch
            result = fetch_func()
            
            if result:
                # Success: cache and record
                self.cache.set(platform_name, result)
                self.metrics.record_platform_success(platform_name, len(result))
                return result
            else:
                # No data: try cache
                cached = self.cache.get(platform_name)
                if cached:
                    logger.info(f"Using cache fallback for {platform_name}")
                    self.metrics.record_platform_success(platform_name, len(cached), 'cache')
                    return cached
                else:
                    self.metrics.record_platform_failure(platform_name, 'No data and no cache')
                    return []
        
        except Exception as e:
            logger.error(f"Error fetching {platform_name}: {e}")
            # Try cache on error
            cached = self.cache.get(platform_name)
            if cached:
                logger.info(f"Using cache fallback after error for {platform_name}")
                self.metrics.record_platform_success(platform_name, len(cached), 'cache')
                return cached
            else:
                self.metrics.record_platform_failure(platform_name, str(e))
                return []

# Global wrapper instance
_fetcher_wrapper = None

def get_fetcher_wrapper(fetcher, config, cache_manager, metrics_tracker):
    """Get or create fetcher wrapper"""
    global _fetcher_wrapper
    if _fetcher_wrapper is None:
        _fetcher_wrapper = FetcherWrapper(fetcher, config, cache_manager, metrics_tracker)
    return _fetcher_wrapper
