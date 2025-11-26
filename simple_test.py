# -*- coding: utf-8 -*-
"""
Simple AI Summary Test
"""
import os
os.environ['GEMINI_API_KEY'] = 'AIzaSyC5PNJXsXhD4lL1ZLNwy_6kVWVj5qxiv3s'

import sys
sys.path.insert(0, 'src')

from ai_summarizer import AISummarizer

print("=" * 60)
print("AI Summarizer Test")
print("=" * 60)

summarizer = AISummarizer()

if summarizer.enabled:
    print("\nOK: AI Summarizer initialized!")
    
    # Test summary generation
    test_title = "美股收盘:谷歌市值逼近4万亿美元"
    print(f"\nTest title: {test_title}")
    print("\nGenerating summary...")
    
    summary = summarizer.generate_summary(test_title)
    
    if summary:
        print("\n[Summary]")
        print(summary)
        print("\nSUCCESS: AI Summary feature works!")
    else:
        print("\nERROR: Failed to generate summary")
else:
    print("\nERROR: AI Summarizer not initialized")
