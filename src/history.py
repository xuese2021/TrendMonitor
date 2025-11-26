import json
import os
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class HistoryManager:
    def __init__(self, history_file='data/history.json', max_items=2000):
        self.history_file = history_file
        self.max_items = max_items
        self.history = self._load_history()

    def _load_history(self):
        """Load history from file and migrate if necessary"""
        # Ensure data directory exists
        os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
        
        if not os.path.exists(self.history_file):
            return []
        
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    return self._migrate_data(data)
                return []
        except Exception as e:
            logger.error(f"Failed to load history: {e}")
            return []

    def _migrate_data(self, data):
        """Migrate old string-only history to object format"""
        migrated = []
        now = datetime.now().isoformat()
        
        for item in data:
            if isinstance(item, str):
                # Old format: just URL
                migrated.append({
                    'url': item,
                    'title': 'Unknown Title',
                    'platform': 'unknown',
                    'timestamp': now
                })
            elif isinstance(item, dict):
                # New format
                migrated.append(item)
                
        return migrated

    def save_history(self):
        """Save history to file"""
        try:
            # Keep only the last max_items
            if len(self.history) > self.max_items:
                self.history = self.history[-self.max_items:]
            
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Failed to save history: {e}")

    def is_sent(self, url):
        """Check if a URL has already been sent"""
        return any(item['url'] == url for item in self.history)

    def add(self, item):
        """Add an item to history"""
        if isinstance(item, str):
            # Backward compatibility
            item = {
                'url': item,
                'title': 'Unknown Title',
                'platform': 'unknown',
                'timestamp': datetime.now().isoformat()
            }
            
        if not self.is_sent(item['url']):
            # Ensure timestamp exists
            if 'timestamp' not in item:
                item['timestamp'] = datetime.now().isoformat()
            self.history.append(item)

    def clean_old(self, days=7):
        """Remove items older than N days"""
        cutoff = datetime.now() - timedelta(days=days)
        original_count = len(self.history)
        
        self.history = [
            item for item in self.history 
            if datetime.fromisoformat(item['timestamp']) > cutoff
        ]
        
        removed = original_count - len(self.history)
        if removed > 0:
            logger.info(f"Cleaned {removed} old items from history")
            self.save_history()

    def get_recent(self, hours=24):
        """Get items from the last N hours"""
        cutoff = datetime.now() - timedelta(hours=hours)
        return [
            item for item in self.history 
            if datetime.fromisoformat(item['timestamp']) > cutoff
        ]
