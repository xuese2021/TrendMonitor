"""
Quick test for AI Summary with API key
"""
import os
os.environ['GEMINI_API_KEY'] = 'AIzaSyC5PNJXsXhD4lL1ZLNwy_6kVWVj5qxiv3s'

import sys
sys.path.insert(0, 'src')

from ai_summarizer import AISummarizer

print("=" * 60)
print("Testing AI Summarizer with your API key")
print("=" * 60)

summarizer = AISummarizer()

if summarizer.enabled:
    print("\n✓ AI Summarizer initialized successfully!\n")
    
    # Test with a real news title
    test_title = "美股收盘:谷歌市值逼近4万亿美元"
    print(f"Generating summary for: {test_title}\n")
    
    summary = summarizer.generate_summary(test_title)
    
    if summary:
        print("📝 Generated Summary:")
        print(f"   {summary}\n")
        print("✅ AI Summary feature is working perfectly!")
    else:
        print("❌ Failed to generate summary")
else:
    print("❌ AI Summarizer failed to initialize")
