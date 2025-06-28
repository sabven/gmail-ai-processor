"""WhatsApp messaging service"""

import logging
import requests
from twilio.rest import Client

logger = logging.getLogger(__name__)

class WhatsAppService:
    """Service for sending WhatsApp messages"""
    
    def __init__(self, config):
        self.config = config
        self._setup_client()
    
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
        """Send WhatsApp message using Twilio or CallMeBot"""
        
        try:
            if self.config.TWILIO_ACCOUNT_SID and self.twilio_client:
                return self._send_via_twilio(message)
            elif self.config.CALLMEBOT_API_KEY:
                return self._send_via_callmebot(message)
            else:
                logger.error("No WhatsApp service configured")
                return False
                
        except Exception as e:
            logger.error(f"Error sending WhatsApp message: {e}")
            return False
    
    def _send_via_twilio(self, message: str) -> bool:
        """Send message via Twilio WhatsApp API"""
        message_obj = self.twilio_client.messages.create(
            body=message,
            from_=self.config.TWILIO_WHATSAPP_NUMBER,
            to=self.config.YOUR_WHATSAPP_NUMBER
        )
        logger.info(f"WhatsApp message sent via Twilio: {message_obj.sid}")
        return True
    
    def _send_via_callmebot(self, message: str) -> bool:
        """Send message via CallMeBot API"""
        url = "https://api.callmebot.com/whatsapp.php"
        params = {
            'phone': self.config.CALLMEBOT_PHONE,
            'text': message,
            'apikey': self.config.CALLMEBOT_API_KEY
        }
        
        response = requests.get(url, params=params)
        if response.status_code == 200:
            logger.info("WhatsApp message sent via CallMeBot")
            return True
        else:
            logger.error(f"CallMeBot error: {response.text}")
            return False
