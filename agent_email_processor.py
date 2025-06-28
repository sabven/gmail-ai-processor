"""Agent-based Email Processor - New architecture using LangChain-style agents"""

import logging
from datetime import datetime
from typing import Dict, Any

from config import Config
from agents.coordinator_agent import CoordinatorAgent

logger = logging.getLogger(__name__)

class AgentEmailProcessor:
    """New agent-based email processor using coordinator and specialized agents"""
    
    def __init__(self, config: Config):
        self.config = config
        self.coordinator = CoordinatorAgent(config)
        self.logger = logging.getLogger(__name__)
        
    def process_emails(self, max_emails: int = 10) -> Dict[str, Any]:
        """Main method to process emails using the agent architecture"""
        self.logger.info("Starting agent-based email processing...")
        
        try:
            # Use the coordinator to orchestrate the entire workflow
            result = self.coordinator.execute({
                "action": "process_all_emails",
                "max_emails": max_emails,
                "send_notifications": True,
                "create_events": True
            })
            
            # Log results
            if result.get("success"):
                self.logger.info(f"Agent workflow completed successfully: {result.get('message')}")
            else:
                self.logger.error(f"Agent workflow failed: {result.get('error')}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error in agent-based email processing: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def process_single_email(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single email using the agent workflow"""
        self.logger.info(f"Processing single email with agents: {email_data.get('subject', 'No Subject')}")
        
        try:
            result = self.coordinator.execute({
                "action": "process_single_email",
                "email_data": email_data,
                "send_notification": True,
                "create_event": True
            })
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error processing single email with agents: {e}")
            return {
                "success": False,
                "error": str(e),
                "email_subject": email_data.get("subject", "Unknown")
            }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status from all agents"""
        self.logger.info("Getting system status from agents...")
        
        try:
            return self.coordinator.execute({"action": "get_workflow_status"})
            
        except Exception as e:
            self.logger.error(f"Error getting system status: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def run_health_check(self) -> Dict[str, Any]:
        """Run comprehensive health check on all services"""
        self.logger.info("Running health check on all services...")
        
        try:
            return self.coordinator.execute({"action": "run_health_check"})
            
        except Exception as e:
            self.logger.error(f"Error running health check: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get information about all available agents and their functions"""
        try:
            return {
                "success": True,
                "coordinator": {
                    "name": self.coordinator.name,
                    "description": self.coordinator.description,
                    "functions": self.coordinator.get_available_functions()
                },
                "agents": {
                    "email_agent": {
                        "name": self.coordinator.email_agent.name,
                        "description": self.coordinator.email_agent.description,
                        "functions": self.coordinator.email_agent.get_available_functions()
                    },
                    "analysis_agent": {
                        "name": self.coordinator.analysis_agent.name,
                        "description": self.coordinator.analysis_agent.description,
                        "functions": self.coordinator.analysis_agent.get_available_functions()
                    },
                    "notification_agent": {
                        "name": self.coordinator.notification_agent.name,
                        "description": self.coordinator.notification_agent.description,
                        "functions": self.coordinator.notification_agent.get_available_functions()
                    },
                    "calendar_agent": {
                        "name": self.coordinator.calendar_agent.name,
                        "description": self.coordinator.calendar_agent.description,
                        "functions": self.coordinator.calendar_agent.get_available_functions()
                    }
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting agent info: {e}")
            return {
                "success": False,
                "error": str(e)
            }
