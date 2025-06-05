#!/usr/bin/env python3
"""
Test script to validate Google Gemini API key before deployment
"""

import os
import sys
from dotenv import load_dotenv

def test_google_api():
    """Test Google Gemini API connection"""
    
    # Load environment variables
    load_dotenv()
    
    # Get API key
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("❌ GOOGLE_API_KEY not found in environment variables")
        print("Please set GOOGLE_API_KEY in your .env file")
        return False
    
    try:
        import google.generativeai as genai
        
        # Configure the API
        genai.configure(api_key=api_key)
        
        # Get model name
        model_name = os.getenv('GOOGLE_MODEL', 'gemini-1.5-flash')
        print(f"🔍 Testing model: {model_name}")
        
        # Create model instance
        model = genai.GenerativeModel(model_name)
        
        # Test with a simple prompt
        test_prompt = "Hello! Please respond with just 'API test successful' to confirm you're working."
        
        print("🚀 Sending test request to Google Gemini...")
        response = model.generate_content(test_prompt)
        
        if response and hasattr(response, 'candidates') and response.candidates:
            candidate = response.candidates[0]
            if hasattr(candidate.content, 'parts') and candidate.content.parts:
                result = candidate.content.parts[0].text
                print(f"✅ API Response: {result}")
                print("✅ Google Gemini API is working correctly!")
                return True
        
        print("⚠️  Received empty response from API")
        return False
        
    except ImportError:
        print("❌ google-generativeai package not installed")
        print("Run: pip install google-generativeai")
        return False
        
    except Exception as e:
        print(f"❌ API test failed: {str(e)}")
        
        # Provide specific error guidance
        if "API_KEY_INVALID" in str(e):
            print("💡 Your API key appears to be invalid")
            print("   Get a new key from: https://makersuite.google.com/app/apikey")
        elif "PERMISSION_DENIED" in str(e):
            print("💡 Permission denied - check if the Gemini API is enabled")
        elif "QUOTA_EXCEEDED" in str(e):
            print("💡 API quota exceeded - check your Google Cloud billing")
        elif "MODEL_NOT_FOUND" in str(e):
            print(f"💡 Model '{model_name}' not found or not available")
            print("   Try using: gemini-1.5-flash or gemini-1.5-pro")
        
        return False

def main():
    print("🔍 Google Gemini API Test")
    print("=" * 30)
    
    if test_google_api():
        print("\n🎉 Ready for deployment!")
        sys.exit(0)
    else:
        print("\n❌ Fix the issues above before deploying")
        sys.exit(1)

if __name__ == "__main__":
    main()