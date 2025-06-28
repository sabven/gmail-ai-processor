"""Email fetching and processing service"""

import imaplib
import email
import logging
from datetime import datetime, timedelta
from typing import Dict, List

logger = logging.getLogger(__name__)

class EmailService:
    """Service for fetching emails from Gmail"""
    
    def __init__(self, config):
        self.config = config
    
    def get_emails_from_gmail(self) -> List[Dict]:
        """Fetch emails from Gmail using IMAP"""
        emails = []
        
        try:
            # Connect to Gmail
            mail = imaplib.IMAP4_SSL(self.config.IMAP_SERVER, self.config.IMAP_PORT)
            mail.login(self.config.GMAIL_USER, self.config.GMAIL_PASSWORD)
            mail.select('inbox')
            
            # Calculate date range
            since_date = (datetime.now() - timedelta(days=self.config.DAYS_BACK)).strftime('%d-%b-%Y')
            
            # Search for emails from specific domain
            search_criteria = f'(FROM "{self.config.EMAIL_DOMAIN}" SINCE {since_date})'
            result, data = mail.search(None, search_criteria)
            
            if result == 'OK':
                email_ids = data[0].split()
                logger.info(f"Found {len(email_ids)} emails from {self.config.EMAIL_DOMAIN}")
                
                for email_id in email_ids[-10:]:  # Process last 10 emails
                    result, msg_data = mail.fetch(email_id, '(RFC822)')
                    
                    if result == 'OK':
                        email_body = msg_data[0][1]
                        email_message = email.message_from_bytes(email_body)
                        
                        # Extract email details
                        email_dict = {
                            'id': email_id.decode(),
                            'subject': email_message.get('Subject', 'No Subject'),
                            'from': email_message.get('From', 'Unknown'),
                            'date': email_message.get('Date', ''),
                            'body': self._extract_email_body(email_message)
                        }
                        emails.append(email_dict)
            
            mail.logout()
            
        except Exception as e:
            logger.error(f"Error fetching emails: {e}")
        
        return emails
    
    def _extract_email_body(self, email_message) -> str:
        """Extract plain text body from email message"""
        body = ""
        
        if email_message.is_multipart():
            for part in email_message.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    break
        else:
            body = email_message.get_payload(decode=True).decode('utf-8', errors='ignore')
        
        return body.strip()
