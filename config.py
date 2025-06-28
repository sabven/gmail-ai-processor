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
    ANTHROPIC_API_KEY: str = os.getenv('ANTHROPIC_API_KEY')
    AI_MODEL: str = 'gpt-4'  # or 'claude-3-sonnet-20240229'
    
    # WhatsApp/Twilio settings
    TWILIO_ACCOUNT_SID: str = os.getenv('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN: str = os.getenv('TWILIO_AUTH_TOKEN')
    TWILIO_WHATSAPP_NUMBER: str = os.getenv('TWILIO_WHATSAPP_NUMBER', 'whatsapp:+14155238886')
    YOUR_WHATSAPP_NUMBER: str = os.getenv('YOUR_WHATSAPP_NUMBER')  # e.g., 'whatsapp:+65123456789'
    
    # Alternative: CallMeBot (simpler)
    CALLMEBOT_API_KEY: str = os.getenv('CALLMEBOT_API_KEY')
    CALLMEBOT_PHONE: str = os.getenv('CALLMEBOT_PHONE')  # Without + sign
    
    # Google Calendar settings
    GOOGLE_CALENDAR_CREDENTIALS_FILE: str = 'credentials.json'
    GOOGLE_CALENDAR_TOKEN_FILE: str = 'token.json'
    CALENDAR_SCOPES: List[str] = field(default_factory=lambda: ['https://www.googleapis.com/auth/calendar'])
    USE_SERVICE_ACCOUNT: bool = False  # Set to True if using service account instead of OAuth
    
    # Email filtering
    EMAIL_DOMAIN: str = '@xxxx.com'  # Changed to Dovercourt domain
    DAYS_BACK: int = 7
