"""
Test script for Google News and AI Summary features
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from fetcher import TrendFetcher

def test_google_news():
    """Test Google News fetching"""
    print("=" * 60)
    print("Testing Google News Integration")
    print("=" * 60)
    
    fetcher = TrendFetcher()
    news = fetcher.fetch_google_news()
    
    print(f"\n✓ Successfully fetched {len(news)} items from Google News\n")
    
    if news:
        print("First 3 items:")
        for i, item in enumerate(news[:3], 1):
            print(f"\n{i}. {item['title']}")
            print(f"   URL: {item['url'][:80]}...")
    else:
        print("⚠ No items fetched")
    
    return len(news) > 0

def test_ai_summarizer():
    """Test AI Summarizer (requires API key)"""
    print("\n" + "=" * 60)
    print("Testing AI Summarizer")
    print("=" * 60)
    
    from ai_summarizer import AISummarizer
    
    summarizer = AISummarizer()
    
    if not summarizer.enabled:
        print("\n⚠ AI Summarizer is disabled (no GEMINI_API_KEY)")
        print("  To enable: set GEMINI_API_KEY environment variable")
        print("  Get your key at: https://aistudio.google.com")
        return False
    
    print("\n✓ AI Summarizer initialized successfully")
    
    # Test with a sample title
    test_title = "美股收盘:谷歌市值逼近4万亿美元"
    print(f"\nGenerating summary for: {test_title}")
    
    summary = summarizer.generate_summary(test_title)
    
    if summary:
        print(f"\n📝 Generated Summary:")
        print(f"   {summary}")
        return True
    else:
        print("\n⚠ Failed to generate summary")
        return False

if __name__ == "__main__":
    print("\n🚀 TrendMonitor Feature Test\n")
    
    # Test Google News
    google_news_ok = test_google_news()
    
    # Test AI Summarizer
    ai_ok = test_ai_summarizer()
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"Google News Integration: {'✓ PASS' if google_news_ok else '✗ FAIL'}")
    print(f"AI Summarizer: {'✓ PASS' if ai_ok else '⚠ DISABLED (no API key)'}")
    print()
