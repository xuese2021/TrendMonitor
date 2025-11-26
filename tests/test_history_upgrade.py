import unittest
import json
import os
import shutil
from datetime import datetime, timedelta
import sys

# Add src to path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from history import HistoryManager

class TestHistoryUpgrade(unittest.TestCase):
    def setUp(self):
        self.test_dir = 'test_data'
        os.makedirs(self.test_dir, exist_ok=True)
        self.history_file = os.path.join(self.test_dir, 'history.json')

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_migration(self):
        # Create old format history
        old_data = [
            "https://example.com/1",
            "https://example.com/2"
        ]
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(old_data, f)

        # Initialize manager
        manager = HistoryManager(self.history_file)
        
        # Check migration
        self.assertEqual(len(manager.history), 2)
        self.assertIsInstance(manager.history[0], dict)
        self.assertEqual(manager.history[0]['url'], "https://example.com/1")
        self.assertEqual(manager.history[0]['title'], "Unknown Title")
        self.assertTrue('timestamp' in manager.history[0])

    def test_add_new_item(self):
        manager = HistoryManager(self.history_file)
        item = {
            'url': 'https://example.com/new',
            'title': 'New Item',
            'platform': 'test',
            'timestamp': datetime.now().isoformat()
        }
        manager.add(item)
        
        self.assertEqual(len(manager.history), 1)
        self.assertEqual(manager.history[0]['title'], 'New Item')

    def test_add_string_backward_compatibility(self):
        manager = HistoryManager(self.history_file)
        manager.add("https://example.com/string")
        
        self.assertEqual(len(manager.history), 1)
        self.assertEqual(manager.history[0]['url'], "https://example.com/string")
        self.assertEqual(manager.history[0]['title'], "Unknown Title")

    def test_clean_old(self):
        manager = HistoryManager(self.history_file)
        
        # Add old item
        old_time = (datetime.now() - timedelta(days=10)).isoformat()
        manager.history.append({
            'url': 'https://example.com/old',
            'title': 'Old',
            'timestamp': old_time
        })
        
        # Add new item
        new_time = datetime.now().isoformat()
        manager.history.append({
            'url': 'https://example.com/new',
            'title': 'New',
            'timestamp': new_time
        })
        
        manager.clean_old(days=7)
        
        self.assertEqual(len(manager.history), 1)
        self.assertEqual(manager.history[0]['url'], 'https://example.com/new')

    def test_get_recent(self):
        manager = HistoryManager(self.history_file)
        
        # Add item from 2 hours ago
        recent_time = (datetime.now() - timedelta(hours=2)).isoformat()
        manager.history.append({
            'url': 'https://example.com/recent',
            'title': 'Recent',
            'timestamp': recent_time
        })
        
        # Add item from 30 hours ago
        old_time = (datetime.now() - timedelta(hours=30)).isoformat()
        manager.history.append({
            'url': 'https://example.com/old',
            'title': 'Old',
            'timestamp': old_time
        })
        
        recent = manager.get_recent(hours=24)
        self.assertEqual(len(recent), 1)
        self.assertEqual(recent[0]['url'], 'https://example.com/recent')

if __name__ == '__main__':
    unittest.main()
