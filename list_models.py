# -*- coding: utf-8 -*-
"""
List available Gemini models
"""
import os
os.environ['GEMINI_API_KEY'] = 'AIzaSyC5PNJXsXhD4lL1ZLNwy_6kVWVj5qxiv3s'

import google.generativeai as genai

genai.configure(api_key=os.environ['GEMINI_API_KEY'])

print("Available Gemini models:")
print("=" * 60)

for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(f"- {model.name}")
        print(f"  Display name: {model.display_name}")
        print()
