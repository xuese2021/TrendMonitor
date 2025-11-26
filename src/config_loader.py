"""
Configuration loader with UA rotation and delay utilities
"""
import json
import os
import random
import time
import logging

logger = logging.getLogger(__name__)

class ScrapingConfig:
    """Load and provide scraping configuration"""
    
    def __init__(self, config_file='config/scraping_config.json'):
        self.config_file = config_file
        self.config = self._load_config()
    
    def _load_config(self):
        """Load configuration from file"""
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = os.path.join(project_root, self.config_file)
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load config: {e}, using defaults")
            return self._get_defaults()
    
    def _get_defaults(self):
        """Get default configuration"""
        return {
            "delays": {
                "between_platforms": [3, 8],
                "between_requests": [2, 5]
            },
            "retry": {
                "max_attempts": 3,
                "backoff_min": 4,
                "backoff_max": 16
            },
            "timeouts": {
                "api": 15,
                "http": 10,
                "browser": 30,
                "rss": 20
            },
            "user_agents": [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ],
            "monitoring": {
                "min_success_rate": 0.7,
                "enable_alerts": True
            }
        }
    
    def get_random_user_agent(self):
        """Get random User-Agent from pool"""
        return random.choice(self.config['user_agents'])
    
    def get_platform_delay(self):
        """Get random delay for between platforms"""
        min_delay, max_delay = self.config['delays']['between_platforms']
        return random.uniform(min_delay, max_delay)
    
    def get_request_delay(self):
        """Get random delay for between requests"""
        min_delay, max_delay = self.config['delays']['between_requests']
        return random.uniform(min_delay, max_delay)
    
    def sleep_between_platforms(self):
        """Sleep with random delay between platforms"""
        delay = self.get_platform_delay()
        logger.debug(f"Sleeping {delay:.2f}s before next platform")
        time.sleep(delay)
    
    def get_timeout(self, tier='http'):
        """Get timeout for specific tier"""
        return self.config['timeouts'].get(tier, 10)
    
    def should_send_alerts(self):
        """Check if alerts are enabled"""
        return self.config['monitoring']['enable_alerts']
    
    def get_min_success_rate(self):
        """Get minimum acceptable success rate"""
        return self.config['monitoring']['min_success_rate']
