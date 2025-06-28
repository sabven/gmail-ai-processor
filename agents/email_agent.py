"""Email Agent - Handles email fetching and processing"""

import logging
from typing import Any, Dict, List

from agents.base_agent import BaseAgentClass
from services.email_service import EmailService

logger = logging.getLogger(__name__)

class EmailAgent(BaseAgentClass):
    """Agent responsible for email operations"""
    
    def __init__(self, config):
        super().__init__(config)
        self.email_service = EmailService(config)
        self.name = "email_agent"
        self.description = "Handles fetching and processing emails from Gmail"
    
    def get_available_functions(self) -> List[Dict[str, Any]]:
        """Return available email functions"""
        return [
            {
                "name": "fetch_emails",
                "description": "Fetch emails from Gmail inbox",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of emails to fetch",
                            "default": 10
                        }
                    }
                }
            },
            {
                "name": "get_email_details",
                "description": "Get detailed information about a specific email",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "email_id": {
                            "type": "string",
                            "description": "The ID of the email to get details for"
                        }
                    },
                    "required": ["email_id"]
                }
            }
        ]
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute email agent functionality"""
        action = input_data.get("action", "fetch_emails")
        
        try:
            if action == "fetch_emails":
                return self.fetch_emails(input_data.get("limit", 10))
            elif action == "get_email_details":
                return self.get_email_details(input_data.get("email_id"))
            else:
                return {"error": f"Unknown action: {action}"}
                
        except Exception as e:
            self.logger.error(f"Error in email agent: {e}")
            return {"error": str(e)}
    
    def fetch_emails(self, limit: int = 10) -> Dict[str, Any]:
        """Fetch emails from Gmail"""
        self.log_action("fetch_emails", {"limit": limit})
        
        try:
            emails = self.email_service.get_emails_from_gmail()
            
            # Limit the number of emails returned
            if limit and len(emails) > limit:
                emails = emails[:limit]
            
            return {
                "success": True,
                "emails": emails,
                "count": len(emails),
                "message": f"Successfully fetched {len(emails)} emails"
            }
            
        except Exception as e:
            self.logger.error(f"Error fetching emails: {e}")
            return {
                "success": False,
                "error": str(e),
                "emails": [],
                "count": 0
            }
    
    def get_email_details(self, email_id: str) -> Dict[str, Any]:
        """Get details for a specific email"""
        self.log_action("get_email_details", {"email_id": email_id})
        
        try:
            # This would be implemented if we need individual email fetching
            # For now, we'll return a placeholder
            return {
                "success": True,
                "message": "Email details functionality not yet implemented",
                "email_id": email_id
            }
            
        except Exception as e:
            self.logger.error(f"Error getting email details: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {
            "name": self.name,
            "description": self.description,
            "status": "active",
            "functions": len(self.get_available_functions())
        }
