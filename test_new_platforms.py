#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test script for new fetcher methods
"""

from src.fetcher import TrendFetcher

def test_new_platforms():
    """Test all new platform fetchers"""
    fetcher = TrendFetcher()
    
    new_platforms = {
        '36氪': fetcher.fetch_36kr,
        '掘金': fetcher.fetch_juejin,
        '少数派': fetcher.fetch_sspai,
        '什么值得买': fetcher.fetch_smzdm,
        '微信读书': fetcher.fetch_weread,
        '机核': fetcher.fetch_gcores,
        'InfoQ': fetcher.fetch_infoq,
        '腾讯新闻': fetcher.fetch_tencent_news,
        'NYTimes': fetcher.fetch_nytimes,
        '9to5Mac': fetcher.fetch_9to5mac,
        '网易新闻热榜': fetcher.fetch_netease_trending,
    }
    
    print("Testing new platform fetchers...")
    print("=" * 60)
    
    for name, func in new_platforms.items():
        print(f"\nTesting {name}...")
        try:
            trends = func()
            if trends:
                print(f"  ✓ Success: Fetched {len(trends)} items")
                print(f"  Sample: {trends[0]['title'][:50]}...")
            else:
                print(f"  ⚠ Warning: No trends returned")
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    print("\n" + "=" * 60)
    print("Testing complete!")

if __name__ == "__main__":
    test_new_platforms()
