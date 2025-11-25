import sys
import os
sys.path.append(os.path.abspath('src'))

print("Testing imports...")
try:
    from history import HistoryManager
    print("HistoryManager imported.")
    from fetcher import TrendFetcher
    print("TrendFetcher imported.")
except Exception as e:
    print(f"Import failed: {e}")
    sys.exit(1)

print("Testing HistoryManager...")
try:
    hm = HistoryManager('data/test_history.json')
    hm.add('http://test.com')
    hm.save_history()
    print("HistoryManager works.")
except Exception as e:
    print(f"HistoryManager failed: {e}")

print("Testing TrendFetcher...")
try:
    fetcher = TrendFetcher()
    # Test one simple source
    print("Fetching Weibo...")
    weibo = fetcher.fetch_weibo()
    print(f"Weibo items: {len(weibo)}")
except Exception as e:
    print(f"TrendFetcher failed: {e}")
