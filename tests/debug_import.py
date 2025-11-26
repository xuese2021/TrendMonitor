import sys
import os
import traceback

# Add src to path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

print("Attempting to import HistoryManager...")
try:
    from history import HistoryManager
    print("Import successful")
    
    # Try to instantiate
    hm = HistoryManager('test_data/history.json')
    print("Instantiation successful")
    
except Exception:
    traceback.print_exc()
