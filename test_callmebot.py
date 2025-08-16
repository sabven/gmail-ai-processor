#!/usr/bin/env python3
"""
Debug CallMeBot API responses
"""

import requests
from config import Config

def test_callmebot_api():
    """Test CallMeBot API with both numbers"""
    config = Config()
    
    # Simple test message
    test_message = "Test message from Gmail AI Processor"
    
    # Test primary number
    print(f"Testing primary number: {config.CALLMEBOT_PHONE}")
    print(f"API Key: {config.CALLMEBOT_API_KEY}")
    
    url = "https://api.callmebot.com/whatsapp.php"
    phone = config.CALLMEBOT_PHONE
    if not phone.startswith('+'):
        phone = f'+{phone}'
    
    params = {
        'phone': phone,
        'text': test_message,
        'apikey': config.CALLMEBOT_API_KEY
    }
    
    try:
        response = requests.get(url, params=params, timeout=30)
        print(f"\nPrimary number response:")
        print(f"Status Code: {response.status_code}")
        print(f"Response Text: {response.text[:500]}")
        print(f"Response starts with '<': {response.text.startswith('<')}")
        
    except Exception as e:
        print(f"Error with primary number: {e}")
    
    # Test secondary number
    if hasattr(config, 'CALLMEBOT_PHONE_2') and config.CALLMEBOT_PHONE_2:
        print(f"\n" + "="*50)
        print(f"Testing secondary number: {config.CALLMEBOT_PHONE_2}")
        print(f"API Key: {config.CALLMEBOT_API_KEY_2}")
        
        phone2 = config.CALLMEBOT_PHONE_2
        if not phone2.startswith('+'):
            phone2 = f'+{phone2}'
        
        params2 = {
            'phone': phone2,
            'text': test_message,
            'apikey': config.CALLMEBOT_API_KEY_2
        }
        
        try:
            response2 = requests.get(url, params=params2, timeout=30)
            print(f"\nSecondary number response:")
            print(f"Status Code: {response2.status_code}")
            print(f"Response Text: {response2.text[:500]}")
            print(f"Response starts with '<': {response2.text.startswith('<')}")
            
        except Exception as e:
            print(f"Error with secondary number: {e}")

if __name__ == "__main__":
    test_callmebot_api()
