import requests
from bs4 import BeautifulSoup
import html

# Test fetching News Hacker RSS
url = "https://api.newshacker.me/rss"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

print(f"正在测试获取 RSS: {url}")
print("=" * 60)

try:
    # Make request
    response = requests.get(url, headers=headers, timeout=15)
    print(f"状态码: {response.status_code}")
    print(f"Content-Type: {response.headers.get('Content-Type', 'N/A')}")
    print(f"响应大小: {len(response.content)} bytes")
    print("=" * 60)
    
    # Parse as XML
    soup = BeautifulSoup(response.content, 'xml')
    
    # Check for items
    items = soup.find_all('item')
    if not items:
        items = soup.find_all('entry')
    
    print(f"找到 {len(items)} 个条目")
    print("=" * 60)
    
    # Display first few items
    for i, item in enumerate(items[:5], 1):
        title_tag = item.find('title')
        link_tag = item.find('link')
        
        if title_tag:
            title = html.unescape(title_tag.get_text().strip())
            print(f"\n条目 {i}:")
            print(f"标题: {title}")
            
            if link_tag:
                link = link_tag.get_text().strip() if link_tag.string else link_tag.get('href', '')
                print(f"链接: {link}")
        print("-" * 60)
    
    # Show raw XML structure (first 1000 chars)
    print("\n原始 XML 结构 (前1000字符):")
    print(response.text[:1000])
    
except requests.exceptions.Timeout:
    print("错误: 请求超时")
except requests.exceptions.RequestException as e:
    print(f"请求错误: {e}")
except Exception as e:
    print(f"解析错误: {e}")
    import traceback
    traceback.print_exc()
