"""
Cache manager for fallback when fetching fails
"""
import json
import os
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class CacheManager:
    def __init__(self, cache_file='data/cache.json', max_age_seconds=3600):
        self.cache_file = cache_file
        self.max_age_seconds = max_age_seconds
        self.cache = self._load_cache()
    
    def _load_cache(self):
        """Load cache from file"""
        os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
        
        if not os.path.exists(self.cache_file):
            return {}
        
        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load cache: {e}")
            return {}
    
    def save_cache(self):
        """Save cache to file"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Failed to save cache: {e}")
    
    def get(self, platform_name):
        """Get cached data if not expired"""
        if platform_name not in self.cache:
            return None
        
        entry = self.cache[platform_name]
        timestamp = datetime.fromisoformat(entry['timestamp'])
        age = (datetime.now() - timestamp).total_seconds()
        
        if age > self.max_age_seconds:
            logger.debug(f"Cache expired for {platform_name} (age: {age}s)")
            return None
        
        logger.info(f"Using cache for {platform_name} (age: {int(age)}s)")
        return entry['data']
    
    def set(self, platform_name, data):
        """Set cache for platform"""
        self.cache[platform_name] = {
            'data': data,
            'timestamp': datetime.now().isoformat()
        }
    
    def cleanup_old(self):
        """Remove expired cache entries"""
        cutoff = datetime.now() - timedelta(seconds=self.max_age_seconds)
        original_count = len(self.cache)
        
        self.cache = {
            name: entry for name, entry in self.cache.items()
            if datetime.fromisoformat(entry['timestamp']) > cutoff
        }
        
        removed = original_count - len(self.cache)
        if removed > 0:
            logger.info(f"Cleaned {removed} expired cache entries")
            self.save_cache()
