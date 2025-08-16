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
            
            # Calculate date range - get emails from last 2 days and filter by exact time later
            since_date = (datetime.now() - timedelta(days=2)).strftime('%d-%b-%Y')
            
            # Search for emails from specific domain
            search_criteria = f'(FROM "{self.config.EMAIL_DOMAIN}" SINCE {since_date})'
            result, data = mail.search(None, search_criteria)
            
            if result == 'OK':
                email_ids = data[0].split()
                logger.info(f"Found {len(email_ids)} emails from {self.config.EMAIL_DOMAIN}")
                
                # Calculate exact 24-hour cutoff time (make it timezone-aware)
                from datetime import timezone
                cutoff_time = datetime.now(timezone.utc) - timedelta(hours=24)
                logger.info(f"Filtering emails from last 24 hours (since {cutoff_time.strftime('%Y-%m-%d %H:%M:%S %Z')})")
                
                filtered_emails = []
                for email_id in email_ids:
                    result, msg_data = mail.fetch(email_id, '(RFC822)')
                    
                    if result == 'OK':
                        email_body = msg_data[0][1]
                        email_message = email.message_from_bytes(email_body)
                        
                        # Parse email date
                        email_date_str = email_message.get('Date', '')
                        try:
                            # Parse email date (format can vary)
                            from email.utils import parsedate_to_datetime
                            email_date = parsedate_to_datetime(email_date_str)
                            
                            # Check if email is within last 24 hours
                            if email_date >= cutoff_time:
                                filtered_emails.append((email_id, email_message, email_date))
                            
                        except Exception as e:
                            logger.warning(f"Could not parse date '{email_date_str}' for email {email_id.decode()}: {e}")
                            # Include email if we can't parse the date (better to include than miss)
                            filtered_emails.append((email_id, email_message, None))
                
                logger.info(f"Found {len(filtered_emails)} emails from last 24 hours")
                
                # Sort by date (most recent first) and process
                filtered_emails.sort(key=lambda x: x[2] if x[2] else datetime.min, reverse=True)
                
                for email_id, email_message, email_date in filtered_emails[-10:]:  # Process last 10 emails
                        
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
