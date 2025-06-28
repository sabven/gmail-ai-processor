"""Main email processor class"""

import time
import logging
from datetime import datetime
from typing import Dict, List

from config import Config
from services.email_service import EmailService
from services.ai_service import AIService
from services.whatsapp_service import WhatsAppService
from services.calendar_service import CalendarService

logger = logging.getLogger(__name__)

class EmailProcessor:
    """Main class for processing emails"""
    
    def __init__(self, config: Config):
        self.config = config
        self.email_service = EmailService(config)
        self.ai_service = AIService(config)
        self.whatsapp_service = WhatsAppService(config)
        self.calendar_service = CalendarService(config)
    
    def process_emails(self):
        """Main method to process all emails"""
        logger.info("Starting email processing...")
        
        # Get emails from Gmail
        emails = self.email_service.get_emails_from_gmail()
        
        if not emails:
            logger.info("No new emails found")
            return
        
        for email_data in emails:
            logger.info(f"Processing email: {email_data['subject']}")
            
            # Process with AI
            ai_result = self.ai_service.process_email_with_ai(email_data)
            
            # Create WhatsApp message
            whatsapp_message = self._create_whatsapp_message(email_data, ai_result)
            
            # Send WhatsApp notification
            self.whatsapp_service.send_whatsapp_message(whatsapp_message)
            
            # Create calendar event if needed
            if ai_result['hasEvent'] and ai_result['eventDetails']:
                self.calendar_service.create_calendar_event(ai_result['eventDetails'], email_data)
            
            # Small delay between processing emails
            time.sleep(2)
        
        logger.info(f"Processed {len(emails)} emails successfully")
    
    def _create_whatsapp_message(self, email_data: Dict, ai_result: Dict) -> str:
        """Create formatted WhatsApp message"""
        return f"""📧 Email Summary:

From: {email_data['from']}
Subject: {email_data['subject']}

📝 Gist: {ai_result['gist']}

{('📅 Calendar event will be created!' if ai_result['hasEvent'] else '')}

Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
