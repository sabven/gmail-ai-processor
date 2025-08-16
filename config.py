"""Configuration settings for the email processor"""

import os
from dataclasses import dataclass, field
from typing import List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@dataclass
class Config:
    """Configuration class for all API credentials and settings"""
    
    # Gmail IMAP settings
    GMAIL_USER: str = os.getenv('GMAIL_USER')
    GMAIL_PASSWORD: str = os.getenv('GMAIL_APP_PASSWORD')  # Use App Password
    IMAP_SERVER: str = 'imap.gmail.com'
    IMAP_PORT: int = 993
    
    # AI/LLM settings
    OPENAI_API_KEY: str = os.getenv('OPENAI_API_KEY')
    AI_MODEL: str = os.getenv('AI_MODEL', 'gpt-4o')  # Default to gpt-4o, can be overridden via environment
    
    # WhatsApp/Twilio settings
    TWILIO_ACCOUNT_SID: str = os.getenv('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN: str = os.getenv('TWILIO_AUTH_TOKEN')
    TWILIO_WHATSAPP_NUMBER: str = os.getenv('TWILIO_WHATSAPP_NUMBER', 'whatsapp:+14155238886')
    YOUR_WHATSAPP_NUMBER: str = os.getenv('YOUR_WHATSAPP_NUMBER')  # e.g., 'whatsapp:+65123456789'
    
    # Alternative: CallMeBot (simpler) - Primary Number
    CALLMEBOT_API_KEY: str = os.getenv('CALLMEBOT_API_KEY')
    CALLMEBOT_PHONE: str = os.getenv('CALLMEBOT_PHONE')  # Without + sign
    
    # CallMeBot Secondary Number
    CALLMEBOT_API_KEY_2: str = os.getenv('CALLMEBOT_API_KEY_2')  # Second API key
    CALLMEBOT_PHONE_2: str = os.getenv('CALLMEBOT_PHONE_2')  # Second phone number
    
    # Google Calendar settings
    GOOGLE_CALENDAR_CREDENTIALS_FILE: str = 'credentials.json'
    GOOGLE_CALENDAR_TOKEN_FILE: str = 'token.json'
    CALENDAR_SCOPES: List[str] = field(default_factory=lambda: ['https://www.googleapis.com/auth/calendar'])
    USE_SERVICE_ACCOUNT: bool = False  # Set to True if using service account instead of OAuth
    
    # Email filtering
    EMAIL_DOMAIN: str = os.getenv('EMAIL_DOMAIN', '@example.com')  # Filter emails from specific domain (e.g., '@company.com'). Leave empty for all emails
    DAYS_BACK: int = int(os.getenv('DAYS_BACK', '1'))  # Check emails from last N days
    
    def __post_init__(self):
        """Post-initialization to handle environment variables and validation"""
        # Set up WhatsApp credentials (prioritize CallMeBot if available)
        if self.CALLMEBOT_API_KEY and self.CALLMEBOT_PHONE:
            self.WHATSAPP_API_KEY = self.CALLMEBOT_API_KEY
            self.WHATSAPP_PHONE = self.CALLMEBOT_PHONE
        elif self.TWILIO_ACCOUNT_SID and self.TWILIO_AUTH_TOKEN:
            self.WHATSAPP_API_KEY = self.TWILIO_AUTH_TOKEN
            self.WHATSAPP_PHONE = self.YOUR_WHATSAPP_NUMBER
        else:
            self.WHATSAPP_API_KEY = None
            self.WHATSAPP_PHONE = None
