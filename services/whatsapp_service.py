"""WhatsApp messaging service"""

import logging
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from twilio.rest import Client

logger = logging.getLogger(__name__)

class WhatsAppService:
    """Service for sending WhatsApp messages"""
    
    def __init__(self, config):
        self.config = config
        self._setup_client()
    
    def _safe_log_message(self, level, message):
        """Safely log messages with Unicode characters, replacing problematic emojis if needed"""
        try:
            getattr(logger, level)(message)
        except UnicodeEncodeError:
            # Replace common emojis with text equivalents for logging
            safe_message = (message.replace('📧', '[EMAIL]')
                                  .replace('📝', '[NOTE]')
                                  .replace('🎯', '[ACTION]')
                                  .replace('🔴', '[HIGH]')
                                  .replace('🟡', '[MEDIUM]')
                                  .replace('🟢', '[LOW]'))
            getattr(logger, level)(safe_message)
    
    def _setup_client(self):
        """Initialize WhatsApp clients"""
        # Twilio client
        if self.config.TWILIO_ACCOUNT_SID and self.config.TWILIO_AUTH_TOKEN:
            self.twilio_client = Client(
                self.config.TWILIO_ACCOUNT_SID, 
                self.config.TWILIO_AUTH_TOKEN
            )
        else:
            self.twilio_client = None
    
    def send_whatsapp_message(self, message: str) -> bool:
        """Send WhatsApp message using Twilio or CallMeBot with fallback options"""
        
        try:
            # Try Twilio first if available
            if self.config.TWILIO_ACCOUNT_SID and self.twilio_client:
                logger.info("Attempting to send via Twilio WhatsApp...")
                if self._send_via_twilio(message):
                    return True
                logger.warning("Twilio failed, trying CallMeBot...")
            
            # Try CallMeBot for all configured numbers
            success_count = 0
            total_attempts = 0
            
            if self.config.CALLMEBOT_API_KEY and self.config.CALLMEBOT_PHONE:
                logger.info("Attempting to send via CallMeBot (Primary)...")
                total_attempts += 1
                if self._send_via_callmebot(message, self.config.CALLMEBOT_PHONE, self.config.CALLMEBOT_API_KEY):
                    success_count += 1
                else:
                    logger.warning("CallMeBot primary number failed")
            
            if self.config.CALLMEBOT_API_KEY_2 and self.config.CALLMEBOT_PHONE_2:
                logger.info("Attempting to send via CallMeBot (Secondary)...")
                total_attempts += 1
                if self._send_via_callmebot(message, self.config.CALLMEBOT_PHONE_2, self.config.CALLMEBOT_API_KEY_2):
                    success_count += 1
                else:
                    logger.warning("CallMeBot secondary number failed")
            
            # Consider success if at least one message was sent
            if success_count > 0:
                logger.info(f"WhatsApp messages sent successfully to {success_count}/{total_attempts} numbers")
                return True
            elif total_attempts > 0:
                logger.warning("All CallMeBot attempts failed, trying email fallback...")
            
            # Fallback: Send email to self as notification
            return self._send_email_fallback(message)
                
        except Exception as e:
            logger.error(f"Error sending WhatsApp message: {e}")
            return self._send_email_fallback(message)
    
    def _send_via_twilio(self, message: str) -> bool:
        """Send message via Twilio WhatsApp API"""
        message_obj = self.twilio_client.messages.create(
            body=message,
            from_=self.config.TWILIO_WHATSAPP_NUMBER,
            to=self.config.YOUR_WHATSAPP_NUMBER
        )
        logger.info(f"WhatsApp message sent via Twilio: {message_obj.sid}")
        return True
    
    def _send_via_callmebot(self, message: str, phone_number: str, api_key: str) -> bool:
        """Send message via CallMeBot API"""
        url = "https://api.callmebot.com/whatsapp.php"
        
        # Ensure phone number has + prefix
        phone = phone_number
        if not phone.startswith('+'):
            phone = f'+{phone}'
        
        params = {
            'phone': phone,
            'text': message,
            'apikey': api_key
        }
        
        try:
            response = requests.get(url, params=params, timeout=30)
            response_text = response.text.strip()
            
            # Check for account paused message
            if "Account is" in response_text and "Paused" in response_text:
                logger.error(f"CallMeBot account for {phone} is paused. Please send 'resume' to the bot to reactivate your account.")
                logger.error("Visit https://api.callmebot.com/whatsapp.php to reactivate your account")
                return False
            
            # Check for success - CallMeBot returns HTML responses
            if response.status_code in [200, 210]:  # 210 = queued due to rate limit
                if "Message queued" in response_text or "messages was added into the queue" in response_text:
                    self._safe_log_message('info', f"WhatsApp message queued successfully via CallMeBot to {phone}")
                    return True
                elif "Account is" in response_text and "Paused" in response_text:
                    self._safe_log_message('error', f"CallMeBot account for {phone} is paused. Please send 'resume' to reactivate.")
                    return False
                elif response_text.startswith('<') and "Message to:" in response_text:
                    # HTML response but contains message confirmation
                    self._safe_log_message('info', f"WhatsApp message processed via CallMeBot to {phone} (HTML response)")
                    return True
                else:
                    self._safe_log_message('warning', f"CallMeBot unexpected response for {phone}: {response_text[:200]}")
                    return False
            else:
                self._safe_log_message('error', f"CallMeBot error for {phone} (Status {response.status_code}): {response_text[:200]}")
                return False
                
        except requests.exceptions.RequestException as e:
            self._safe_log_message('error', f"CallMeBot network error for {phone}: {e}")
            return False
    
    def _send_email_fallback(self, message: str) -> bool:
        """Fallback: Send email notification when WhatsApp services fail"""
        try:
            if not self.config.GMAIL_USER or not self.config.GMAIL_PASSWORD:
                logger.error("No email credentials for fallback notification")
                return False
            
            # Create email message
            msg = MIMEMultipart()
            msg['From'] = self.config.GMAIL_USER
            msg['To'] = self.config.GMAIL_USER  # Send to self
            msg['Subject'] = "Gmail AI Processor - WhatsApp Failed (Email Fallback)"
            
            body = f"""WhatsApp notification services are currently unavailable.
            
Here's your email notification instead:

{message}

---
This is a fallback email notification because:
- CallMeBot service is paused
- Please reactivate CallMeBot by sending 'resume' to your WhatsApp bot

Email sent from Gmail AI Processor"""
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email using Gmail SMTP
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(self.config.GMAIL_USER, self.config.GMAIL_PASSWORD)
            
            text = msg.as_string()
            server.sendmail(self.config.GMAIL_USER, self.config.GMAIL_USER, text)
            server.quit()
            
            logger.info("Email fallback notification sent successfully")
            return True
            
        except Exception as e:
            logger.error(f"Email fallback also failed: {e}")
            return False
