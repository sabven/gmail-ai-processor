"""Notification Agent - Handles WhatsApp and other notifications"""

import logging
from datetime import datetime
from typing import Any, Dict, List

from agents.base_agent import BaseAgentClass
from services.whatsapp_service import WhatsAppService

logger = logging.getLogger(__name__)

class NotificationAgent(BaseAgentClass):
    """Agent responsible for sending notifications"""
    
    def __init__(self, config):
        super().__init__(config)
        self.whatsapp_service = WhatsAppService(config)
        self.name = "notification_agent"
        self.description = "Handles sending WhatsApp and other notifications"
    
    def get_available_functions(self) -> List[Dict[str, Any]]:
        """Return available notification functions"""
        return [
            {
                "name": "send_whatsapp_notification",
                "description": "Send a WhatsApp notification message",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "message": {
                            "type": "string",
                            "description": "The message to send via WhatsApp"
                        },
                        "recipient": {
                            "type": "string",
                            "description": "Recipient phone number (optional, uses config default)",
                            "default": None
                        }
                    },
                    "required": ["message"]
                }
            },
            {
                "name": "create_email_summary_notification",
                "description": "Create a formatted notification for email summary",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "email_data": {
                            "type": "object",
                            "description": "Email data",
                            "properties": {
                                "subject": {"type": "string"},
                                "from": {"type": "string"}
                            }
                        },
                        "analysis_result": {
                            "type": "object",
                            "description": "AI analysis result",
                            "properties": {
                                "gist": {"type": "string"},
                                "hasEvent": {"type": "boolean"}
                            }
                        }
                    },
                    "required": ["email_data", "analysis_result"]
                }
            },
            {
                "name": "send_bulk_notifications",
                "description": "Send multiple notifications at once",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "notifications": {
                            "type": "array",
                            "description": "List of notification messages to send",
                            "items": {"type": "string"}
                        }
                    },
                    "required": ["notifications"]
                }
            }
        ]
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute notification agent functionality"""
        action = input_data.get("action", "send_whatsapp_notification")
        
        try:
            if action == "send_whatsapp_notification":
                return self.send_whatsapp_notification(
                    input_data.get("message"),
                    input_data.get("recipient")
                )
            elif action == "create_email_summary_notification":
                return self.create_email_summary_notification(
                    input_data.get("email_data"),
                    input_data.get("analysis_result")
                )
            elif action == "send_bulk_notifications":
                return self.send_bulk_notifications(input_data.get("notifications"))
            else:
                return {"error": f"Unknown action: {action}"}
                
        except Exception as e:
            self.logger.error(f"Error in notification agent: {e}")
            return {"error": str(e)}
    
    def send_whatsapp_notification(self, message: str, recipient: str = None) -> Dict[str, Any]:
        """Send a WhatsApp notification"""
        self.log_action("send_whatsapp_notification", {"message_length": len(message)})
        
        try:
            success = self.whatsapp_service.send_whatsapp_message(message)
            
            return {
                "success": success,
                "message": "WhatsApp notification sent successfully" if success else "Failed to send WhatsApp notification",
                "timestamp": datetime.now().isoformat(),
                "message_length": len(message)
            }
            
        except Exception as e:
            self.logger.error(f"Error sending WhatsApp notification: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def create_email_summary_notification(self, email_data: Dict[str, Any], analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Create a formatted notification for email summary"""
        self.log_action("create_email_summary_notification", {"subject": email_data.get("subject")})
        
        try:
            # Create formatted message
            message = self._format_email_notification(email_data, analysis_result)
            
            # Send the notification
            result = self.send_whatsapp_notification(message)
            result["formatted_message"] = message
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error creating email summary notification: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def send_bulk_notifications(self, notifications: List[str]) -> Dict[str, Any]:
        """Send multiple notifications"""
        self.log_action("send_bulk_notifications", {"count": len(notifications)})
        
        results = []
        successful = 0
        
        for i, message in enumerate(notifications):
            try:
                result = self.send_whatsapp_notification(message)
                results.append({
                    "index": i,
                    "success": result["success"],
                    "message": message[:50] + "..." if len(message) > 50 else message
                })
                
                if result["success"]:
                    successful += 1
                    
                # Small delay between messages
                import time
                time.sleep(1)
                
            except Exception as e:
                results.append({
                    "index": i,
                    "success": False,
                    "error": str(e)
                })
        
        return {
            "success": successful > 0,
            "total_notifications": len(notifications),
            "successful": successful,
            "failed": len(notifications) - successful,
            "results": results
        }
    
    def _format_email_notification(self, email_data: Dict[str, Any], analysis_result: Dict[str, Any]) -> str:
        """Format email data and analysis into notification message"""
        message = f"""📧 Email Summary:

From: {email_data.get('from', 'Unknown')}
Subject: {email_data.get('subject', 'No Subject')}

📝 Gist: {analysis_result.get('gist', 'No summary available')}"""
        
        # Add event information if available
        if analysis_result.get('hasEvent'):
            message += "\n\n📅 Calendar event will be created!"
        
        # Add priority if available
        if analysis_result.get('priority'):
            priority_emoji = "🔴" if analysis_result['priority'] == 'high' else "🟡" if analysis_result['priority'] == 'medium' else "🟢"
            message += f"\n\n{priority_emoji} Priority: {analysis_result['priority'].title()}"
        
        # Add action items if available
        if analysis_result.get('actionItems') and len(analysis_result['actionItems']) > 0:
            message += "\n\n✅ Action Items:"
            for item in analysis_result['actionItems'][:3]:  # Limit to 3 items
                message += f"\n• {item}"
        
        # Add timestamp
        message += f"\n\nTime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        return message
    
    def create_system_notification(self, title: str, content: str, notification_type: str = "info") -> Dict[str, Any]:
        """Create a system notification"""
        self.log_action("create_system_notification", {"type": notification_type})
        
        try:
            # Create emoji based on type
            emoji_map = {
                "info": "ℹ️",
                "success": "✅",
                "warning": "⚠️", 
                "error": "❌",
                "alert": "🚨"
            }
            
            emoji = emoji_map.get(notification_type, "📢")
            
            message = f"""{emoji} {title}

{content}

Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
            
            return self.send_whatsapp_notification(message)
            
        except Exception as e:
            self.logger.error(f"Error creating system notification: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        # Check if either Twilio or CallMeBot is configured
        twilio_configured = bool(self.config.TWILIO_ACCOUNT_SID and self.config.TWILIO_AUTH_TOKEN and self.config.YOUR_WHATSAPP_NUMBER)
        callmebot_configured = bool(self.config.CALLMEBOT_API_KEY and self.config.CALLMEBOT_PHONE)
        whatsapp_configured = twilio_configured or callmebot_configured
        
        return {
            "name": self.name,
            "description": self.description,
            "status": "active",
            "functions": len(self.get_available_functions()),
            "whatsapp_configured": whatsapp_configured,
            "twilio_configured": twilio_configured,
            "callmebot_configured": callmebot_configured
        }
