import sys
import os

print(f"Python version: {sys.version}")
print(f"Executable: {sys.executable}")
print(f"CWD: {os.getcwd()}")

try:
    import requests
    print("requests module found")
except ImportError:
    print("requests module NOT found")
