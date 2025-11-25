import sys, traceback, os
sys.path.append(os.path.abspath('src'))
try:
    from src import main
    main.main()
except Exception:
    traceback.print_exc()
