import json
import os
import logging

logger = logging.getLogger(__name__)

class HistoryManager:
    def __init__(self, history_file='data/history.json', max_items=1000):
        self.history_file = history_file
        self.max_items = max_items
        self.history = self._load_history()

    def _load_history(self):
        """Load history from file"""
        # Ensure data directory exists
        os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
        
        if not os.path.exists(self.history_file):
            return []
        
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
                return []
        except Exception as e:
            logger.error(f"Failed to load history: {e}")
            return []

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
        return url in self.history

    def add(self, url):
        """Add a URL to history"""
        if url not in self.history:
            self.history.append(url)
