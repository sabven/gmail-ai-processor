#!/usr/bin/env python3
"""
Gmail to AI Agent to WhatsApp and Calendar Processor
Runs daily at 5 PM to process emails from @dcis.com domain
"""

import os
import logging
import schedule
import time

from config import Config
from email_processor import EmailProcessor

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('email_processor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def create_env_file():
    """Create a sample .env file with all required variables"""
    env_content = """# Gmail IMAP Configuration
GMAIL_USER=your_email@gmail.com
GMAIL_APP_PASSWORD=your_app_password  # Generate this in Gmail settings

# AI/LLM Configuration (choose one)
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key

# WhatsApp via Twilio (Option 1)
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
YOUR_WHATSAPP_NUMBER=whatsapp:+65123456789

# WhatsApp via CallMeBot (Option 2 - Simpler)
CALLMEBOT_API_KEY=your_callmebot_api_key
CALLMEBOT_PHONE=65123456789

# Google Calendar (download credentials.json from Google Cloud Console)
# Place credentials.json in the same directory as this script
"""
    
    with open('.env.example', 'w') as f:
        f.write(env_content)
    
    print("Created .env.example file. Please copy it to .env and fill in your credentials.")

def main():
    """Main function to run the email processor"""
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("No .env file found. Creating example...")
        create_env_file()
        return
    
    # Initialize configuration
    config = Config()
    
    # Validate required configuration
    if not config.GMAIL_USER or not config.GMAIL_PASSWORD:
        logger.error("Gmail credentials not configured")
        return
    
    if not config.OPENAI_API_KEY and not config.ANTHROPIC_API_KEY:
        logger.error("No AI API key configured")
        return
    
    # Initialize email processor
    processor = EmailProcessor(config)
    
    # Schedule the job to run daily at 5 PM (commented out for immediate testing)
    # schedule.every().day.at("17:00").do(processor.process_emails)
    
    # For testing, run immediately
    logger.info("Running email processing immediately...")
    processor.process_emails()
    
    logger.info("Email processing completed. To enable scheduled runs, uncomment the schedule line.")
    
    # Commented out the infinite loop for testing
    # logger.info("Email processor started. Scheduled to run daily at 5 PM.")
    # logger.info("Press Ctrl+C to stop.")
    # 
    # try:
    #     while True:
    #         schedule.run_pending()
    #         time.sleep(60)  # Check every minute
    # except KeyboardInterrupt:
    #     logger.info("Email processor stopped.")

if __name__ == "__main__":
    main()
