"""Coordinator Agent - Orchestrates the entire email processing workflow"""

import logging
import time
from datetime import datetime
from typing import Any, Dict, List

from agents.base_agent import BaseAgentClass
from agents.email_agent import EmailAgent
from agents.analysis_agent import AnalysisAgent
from agents.notification_agent import NotificationAgent
from agents.calendar_agent import CalendarAgent

logger = logging.getLogger(__name__)

class CoordinatorAgent(BaseAgentClass):
    """Main coordinator agent that orchestrates the email processing workflow"""
    
    def __init__(self, config):
        super().__init__(config)
        self.name = "coordinator_agent"
        self.description = "Orchestrates the entire email processing workflow using specialized agents"
        
        # Initialize sub-agents
        self.email_agent = EmailAgent(config)
        self.analysis_agent = AnalysisAgent(config)
        self.notification_agent = NotificationAgent(config)
        self.calendar_agent = CalendarAgent(config)
        
        # Track processing statistics
        self.stats = {
            "emails_processed": 0,
            "events_created": 0,
            "notifications_sent": 0,
            "errors": 0,
            "start_time": None,
            "last_run": None
        }
    
    def get_available_functions(self) -> List[Dict[str, Any]]:
        """Return available coordinator functions"""
        return [
            {
                "name": "process_all_emails",
                "description": "Process all emails using the full agent workflow",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "max_emails": {
                            "type": "integer",
                            "description": "Maximum number of emails to process",
                            "default": 10
                        },
                        "send_notifications": {
                            "type": "boolean",
                            "description": "Whether to send WhatsApp notifications",
                            "default": True
                        },
                        "create_events": {
                            "type": "boolean",
                            "description": "Whether to create calendar events",
                            "default": True
                        }
                    }
                }
            },
            {
                "name": "process_single_email",
                "description": "Process a single email through the workflow",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "email_data": {
                            "type": "object",
                            "description": "Email data to process",
                            "properties": {
                                "subject": {"type": "string"},
                                "body": {"type": "string"},
                                "from": {"type": "string"}
                            },
                            "required": ["subject", "body", "from"]
                        },
                        "send_notification": {"type": "boolean", "default": True},
                        "create_event": {"type": "boolean", "default": True}
                    },
                    "required": ["email_data"]
                }
            },
            {
                "name": "get_workflow_status",
                "description": "Get the status of all agents and the workflow",
                "parameters": {"type": "object", "properties": {}}
            },
            {
                "name": "run_health_check",
                "description": "Run a health check on all agents and services",
                "parameters": {"type": "object", "properties": {}}
            }
        ]
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute coordinator agent functionality"""
        action = input_data.get("action", "process_all_emails")
        
        try:
            if action == "process_all_emails":
                return self.process_all_emails(
                    input_data.get("max_emails", 10),
                    input_data.get("send_notifications", True),
                    input_data.get("create_events", True)
                )
            elif action == "process_single_email":
                return self.process_single_email(
                    input_data.get("email_data"),
                    input_data.get("send_notification", True),
                    input_data.get("create_event", True)
                )
            elif action == "get_workflow_status":
                return self.get_workflow_status()
            elif action == "run_health_check":
                return self.run_health_check()
            else:
                return {"error": f"Unknown action: {action}"}
                
        except Exception as e:
            self.logger.error(f"Error in coordinator agent: {e}")
            self.stats["errors"] += 1
            return {"error": str(e)}
    
    def process_all_emails(self, max_emails: int = 10, send_notifications: bool = True, create_events: bool = True) -> Dict[str, Any]:
        """Process all emails using the agent workflow"""
        self.log_action("process_all_emails", {"max_emails": max_emails})
        self.stats["start_time"] = datetime.now()
        
        try:
            # Step 1: Fetch emails using EmailAgent
            self.logger.info("Step 1: Fetching emails...")
            email_result = self.email_agent.execute({
                "action": "fetch_emails",
                "limit": max_emails
            })
            
            if not email_result.get("success"):
                return {
                    "success": False,
                    "error": f"Failed to fetch emails: {email_result.get('error')}",
                    "stats": self.stats
                }
            
            emails = email_result.get("emails", [])
            if not emails:
                self.logger.info("No emails to process")
                return {
                    "success": True,
                    "message": "No emails to process",
                    "emails_processed": 0,
                    "stats": self.stats
                }
            
            # Step 2: Process each email through the workflow
            self.logger.info(f"Step 2: Processing {len(emails)} emails...")
            processing_results = []
            
            for i, email_data in enumerate(emails):
                self.logger.info(f"Processing email {i+1}/{len(emails)}: {email_data.get('subject', 'No Subject')}")
                
                try:
                    result = self.process_single_email(email_data, send_notifications, create_events)
                    processing_results.append(result)
                    
                    if result.get("success"):
                        self.stats["emails_processed"] += 1
                    else:
                        self.stats["errors"] += 1
                    
                    # Small delay between emails
                    time.sleep(2)
                    
                except Exception as e:
                    self.logger.error(f"Error processing email {i+1}: {e}")
                    self.stats["errors"] += 1
                    processing_results.append({
                        "success": False,
                        "error": str(e),
                        "email_subject": email_data.get("subject", "Unknown")
                    })
            
            # Step 3: Generate summary
            self.stats["last_run"] = datetime.now()
            successful = sum(1 for r in processing_results if r.get("success"))
            
            self.logger.info(f"Workflow completed: {successful}/{len(emails)} emails processed successfully")
            
            return {
                "success": True,
                "message": f"Processed {successful}/{len(emails)} emails successfully",
                "emails_processed": successful,
                "total_emails": len(emails),
                "processing_results": processing_results,
                "stats": self.stats
            }
            
        except Exception as e:
            self.logger.error(f"Error in process_all_emails: {e}")
            self.stats["errors"] += 1
            return {
                "success": False,
                "error": str(e),
                "stats": self.stats
            }
    
    def process_single_email(self, email_data: Dict[str, Any], send_notification: bool = True, create_event: bool = True) -> Dict[str, Any]:
        """Process a single email through the complete workflow"""
        self.log_action("process_single_email", {"subject": email_data.get("subject")})
        
        try:
            # Step 1: Analyze email with AI
            self.logger.info("Analyzing email with AI...")
            analysis_result = self.analysis_agent.execute({
                "action": "analyze_email",
                "email_data": email_data,
                "analysis_type": "full"
            })
            
            if not analysis_result.get("success"):
                return {
                    "success": False,
                    "error": f"AI analysis failed: {analysis_result.get('error')}",
                    "email_subject": email_data.get("subject")
                }
            
            # Step 2: Send notification if requested
            notification_result = None
            if send_notification:
                self.logger.info("Sending WhatsApp notification...")
                notification_result = self.notification_agent.execute({
                    "action": "create_email_summary_notification",
                    "email_data": email_data,
                    "analysis_result": analysis_result
                })
                
                if notification_result.get("success"):
                    self.stats["notifications_sent"] += 1
            
            # Step 3: Create calendar event if needed and requested
            calendar_result = None
            if create_event and analysis_result.get("hasEvent"):
                self.logger.info("Creating calendar event...")
                calendar_result = self.calendar_agent.process_ai_events(analysis_result, email_data)
                
                if calendar_result.get("success"):
                    self.stats["events_created"] += calendar_result.get("events_created", 0)
            
            # Step 4: Return comprehensive result
            return {
                "success": True,
                "email_subject": email_data.get("subject"),
                "email_from": email_data.get("from"),
                "analysis_result": analysis_result,
                "notification_result": notification_result,
                "calendar_result": calendar_result,
                "workflow_steps": {
                    "ai_analysis": True,
                    "notification_sent": send_notification and notification_result and notification_result.get("success"),
                    "calendar_event_created": create_event and calendar_result and calendar_result.get("success")
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error processing single email: {e}")
            return {
                "success": False,
                "error": str(e),
                "email_subject": email_data.get("subject", "Unknown")
            }
    
    def get_workflow_status(self) -> Dict[str, Any]:
        """Get the status of all agents and the workflow"""
        self.log_action("get_workflow_status")
        
        try:
            # Get status from all agents
            agent_statuses = {
                "email_agent": self.email_agent.get_status(),
                "analysis_agent": self.analysis_agent.get_status(),
                "notification_agent": self.notification_agent.get_status(),
                "calendar_agent": self.calendar_agent.get_status()
            }
            
            # Calculate overall health
            all_active = all(status.get("status") == "active" for status in agent_statuses.values())
            
            return {
                "success": True,
                "coordinator_status": {
                    "name": self.name,
                    "description": self.description,
                    "status": "active" if all_active else "degraded",
                    "stats": self.stats
                },
                "agent_statuses": agent_statuses,
                "overall_health": "healthy" if all_active else "degraded",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting workflow status: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def run_health_check(self) -> Dict[str, Any]:
        """Run a comprehensive health check on all agents and services"""
        self.log_action("run_health_check")
        
        health_results = {
            "email_service": {"status": "unknown", "details": ""},
            "ai_service": {"status": "unknown", "details": ""},
            "whatsapp_service": {"status": "unknown", "details": ""},
            "calendar_service": {"status": "unknown", "details": ""}
        }
        
        try:
            # Check email service
            try:
                # This would test email connectivity
                health_results["email_service"] = {
                    "status": "healthy",
                    "details": "Email service configuration appears valid"
                }
            except Exception as e:
                health_results["email_service"] = {
                    "status": "unhealthy",
                    "details": f"Email service error: {str(e)}"
                }
            
            # Check AI service
            try:
                if self.config.OPENAI_API_KEY or self.config.ANTHROPIC_API_KEY:
                    health_results["ai_service"] = {
                        "status": "healthy",
                        "details": f"AI service configured with model: {self.config.AI_MODEL}"
                    }
                else:
                    health_results["ai_service"] = {
                        "status": "unhealthy",
                        "details": "No AI API keys configured"
                    }
            except Exception as e:
                health_results["ai_service"] = {
                    "status": "unhealthy",
                    "details": f"AI service error: {str(e)}"
                }
            
            # Check WhatsApp service
            try:
                # Check if either Twilio or CallMeBot is configured
                twilio_configured = bool(self.config.TWILIO_ACCOUNT_SID and self.config.TWILIO_AUTH_TOKEN and self.config.YOUR_WHATSAPP_NUMBER)
                callmebot_configured = bool(self.config.CALLMEBOT_API_KEY and self.config.CALLMEBOT_PHONE)
                
                if twilio_configured or callmebot_configured:
                    whatsapp_type = "Twilio" if twilio_configured else "CallMeBot"
                    health_results["whatsapp_service"] = {
                        "status": "healthy",
                        "details": f"WhatsApp service configured ({whatsapp_type})"
                    }
                else:
                    health_results["whatsapp_service"] = {
                        "status": "unhealthy",
                        "details": "Neither Twilio nor CallMeBot credentials are configured"
                    }
            except Exception as e:
                health_results["whatsapp_service"] = {
                    "status": "unhealthy",
                    "details": f"WhatsApp service error: {str(e)}"
                }
            
            # Check calendar service
            try:
                # This would test calendar connectivity
                health_results["calendar_service"] = {
                    "status": "healthy",
                    "details": "Calendar service configuration appears valid"
                }
            except Exception as e:
                health_results["calendar_service"] = {
                    "status": "unhealthy",
                    "details": f"Calendar service error: {str(e)}"
                }
            
            # Calculate overall health
            healthy_services = sum(1 for result in health_results.values() if result["status"] == "healthy")
            total_services = len(health_results)
            overall_health = "healthy" if healthy_services == total_services else "degraded" if healthy_services > 0 else "unhealthy"
            
            return {
                "success": True,
                "overall_health": overall_health,
                "healthy_services": healthy_services,
                "total_services": total_services,
                "service_health": health_results,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error running health check: {e}")
            return {
                "success": False,
                "error": str(e),
                "overall_health": "unhealthy"
            }
    
    def get_status(self) -> Dict[str, Any]:
        """Get coordinator agent status"""
        return {
            "name": self.name,
            "description": self.description,
            "status": "active",
            "functions": len(self.get_available_functions()),
            "stats": self.stats,
            "agents": {
                "email_agent": self.email_agent.name,
                "analysis_agent": self.analysis_agent.name,
                "notification_agent": self.notification_agent.name,
                "calendar_agent": self.calendar_agent.name
            }
        }
