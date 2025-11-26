#!/usr/bin/env python3
"""
RSS Feed Debug Script
用于诊断特定RSS源的抓取问题
"""

import requests
from bs4 import BeautifulSoup
import html
import sys

def test_rss_feed(url, name="测试RSS"):
    """测试单个RSS源"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    print(f"\n{'='*70}")
    print(f"测试RSS源: {name}")
    print(f"URL: {url}")
    print(f"{'='*70}\n")
    
    try:
        # 发送请求
        print("1. 发送HTTP请求...")
        response = requests.get(url, headers=headers, timeout=30)
        
        print(f"   ✓ 状态码: {response.status_code}")
        print(f"   ✓ Content-Type: {response.headers.get('Content-Type', 'N/A')}")
        print(f"   ✓ 响应大小: {len(response.content)} bytes")
        print(f"   ✓ 编码: {response.encoding}")
        
        if response.status_code != 200:
            print(f"\n   ✗ 错误: HTTP状态码 {response.status_code}")
            return False
        
        # 解析XML
        print("\n2. 解析XML...")
        try:
            soup = BeautifulSoup(response.content, 'lxml-xml')
            print("   ✓ 使用 lxml-xml 解析器")
        except:
            soup = BeautifulSoup(response.content, 'xml')
            print("   ✓ 使用 xml 解析器")
        
        # 查找条目
        print("\n3. 查找RSS条目...")
        items = soup.find_all('item')
        if not items:
            items = soup.find_all('entry')
            item_type = "entry (Atom格式)"
        else:
            item_type = "item (RSS格式)"
        
        print(f"   ✓ 找到 {len(items)} 个 {item_type}")
        
        if len(items) == 0:
            print("\n   ✗ 警告: 没有找到任何条目")
            print("\n   XML结构预览 (前1000字符):")
            print("   " + "-"*66)
            print("   " + response.text[:1000].replace("\n", "\n   "))
            return False
        
        # 显示前5个条目
        print("\n4. 解析条目内容...")
        for i, item in enumerate(items[:5], 1):
            title_tag = item.find('title')
            link_tag = item.find('link')
            
            print(f"\n   条目 {i}:")
            if title_tag:
                title = html.unescape(title_tag.get_text().strip())
                print(f"   标题: {title}")
            else:
                print(f"   标题: [未找到]")
            
            if link_tag:
                link = link_tag.get_text().strip() if link_tag.string else link_tag.get('href', '')
                print(f"   链接: {link}")
            else:
                print(f"   链接: [未找到]")
        
        print(f"\n{'='*70}")
        print(f"✓ 测试成功! RSS源 '{name}' 工作正常")
        print(f"{'='*70}\n")
        return True
        
    except requests.exceptions.Timeout:
        print(f"\n✗ 错误: 请求超时 (超过30秒)")
        return False
    except requests.exceptions.ConnectionError as e:
        print(f"\n✗ 错误: 连接失败")
        print(f"   详情: {e}")
        return False
    except requests.exceptions.RequestException as e:
        print(f"\n✗ 错误: 网络请求失败")
        print(f"   详情: {e}")
        return False
    except Exception as e:
        print(f"\n✗ 错误: 解析失败")
        print(f"   详情: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    # 默认测试 News Hacker RSS
    test_feeds = [
        ("News Hacker", "https://api.newshacker.me/rss"),
    ]
    
    # 如果提供了命令行参数,测试指定的URL
    if len(sys.argv) > 1:
        url = sys.argv[1]
        name = sys.argv[2] if len(sys.argv) > 2 else "自定义RSS"
        test_feeds = [(name, url)]
    
    print("\n" + "="*70)
    print("RSS Feed 调试工具")
    print("="*70)
    
    results = []
    for name, url in test_feeds:
        success = test_rss_feed(url, name)
        results.append((name, success))
    
    # 总结
    print("\n" + "="*70)
    print("测试总结")
    print("="*70)
    for name, success in results:
        status = "✓ 成功" if success else "✗ 失败"
        print(f"{status}: {name}")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
