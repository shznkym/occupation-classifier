#!/usr/bin/env python3
"""
Test script to verify Gemini API model compatibility
"""
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_gemini_models():
    """Test available Gemini models and find the correct one"""
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        print("❌ GEMINI_API_KEY not set in environment")
        print("Please set it with: export GEMINI_API_KEY='your_key_here'")
        return False
    
    print("🔑 API Key found, configuring Gemini...")
    genai.configure(api_key=api_key)
    
    print("\n📋 Listing available models that support generateContent:\n")
    
    working_models = []
    for model in genai.list_models():
        if 'generateContent' in model.supported_generation_methods:
            print(f"✓ {model.name}")
            working_models.append(model.name)
    
    if not working_models:
        print("\n❌ No models found that support generateContent")
        return False
    
    # Test each model
    print("\n🧪 Testing models with a simple query...\n")
    test_prompt = "これは何ですか？: 消防車"
    
    for model_name in working_models[:3]:  # Test first 3 models
        try:
            print(f"Testing {model_name}...")
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(test_prompt)
            print(f"  ✓ SUCCESS: {response.text[:100]}...")
            print(f"  👍 Recommended model: {model_name}\n")
            return model_name
        except Exception as e:
            print(f"  ✗ FAILED: {str(e)[:100]}\n")
    
    return None

if __name__ == "__main__":
    recommended_model = test_gemini_models()
    
    if recommended_model:
        print(f"\n✅ Recommended model to use: {recommended_model}")
        print(f"\nUpdate classifier.py with:")
        print(f'    self.llm_model = "{recommended_model}"')
    else:
        print("\n❌ Could not find a working model")
        sys.exit(1)
