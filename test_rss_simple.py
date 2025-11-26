import requests

url = "https://api.newshacker.me/rss"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

try:
    print(f"Fetching: {url}")
    response = requests.get(url, headers=headers, timeout=15)
    print(f"Status: {response.status_code}")
    print(f"Content-Type: {response.headers.get('Content-Type')}")
    print(f"\nFirst 2000 characters of response:")
    print(response.text[:2000])
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
