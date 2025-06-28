#!/usr/bin/env python3
"""
Simple test script to verify the email processor structure works
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import Config
from email_processor import EmailProcessor

def test_basic_functionality():
    """Test basic functionality without actually running the services"""
    print("🔧 Testing Email Processor Structure...")
    
    try:
        # Test configuration loading
        config = Config()
        print("✅ Configuration loaded successfully")
        
        # Test email processor initialization
        processor = EmailProcessor(config)
        print("✅ Email processor initialized successfully")
        
        # Test individual service initialization
        print(f"✅ Email service: {type(processor.email_service).__name__}")
        print(f"✅ AI service: {type(processor.ai_service).__name__}")
        print(f"✅ WhatsApp service: {type(processor.whatsapp_service).__name__}")
        print(f"✅ Calendar service: {type(processor.calendar_service).__name__}")
        
        print("\n🎉 All components initialized successfully!")
        print("\n📋 Next steps:")
        print("1. Copy .env.example to .env")
        print("2. Fill in your credentials in .env")
        print("3. Run: python main.py")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n🔍 Make sure all dependencies are installed:")
        print("pip install -r requirements.txt")

if __name__ == "__main__":
    test_basic_functionality()
