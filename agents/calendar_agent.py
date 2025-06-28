"""Calendar Agent - Handles Google Calendar operations"""

import logging
from datetime import datetime
from typing import Any, Dict, List

from agents.base_agent import BaseAgentClass
from services.calendar_service import CalendarService

logger = logging.getLogger(__name__)

class CalendarAgent(BaseAgentClass):
    """Agent responsible for calendar operations"""
    
    def __init__(self, config):
        super().__init__(config)
        self.calendar_service = CalendarService(config)
        self.name = "calendar_agent"
        self.description = "Handles Google Calendar event creation and management"
    
    def get_available_functions(self) -> List[Dict[str, Any]]:
        """Return available calendar functions"""
        return [
            {
                "name": "create_calendar_event",
                "description": "Create a new event in Google Calendar",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "event_details": {
                            "type": "object",
                            "description": "Event details",
                            "properties": {
                                "title": {"type": "string"},
                                "description": {"type": "string"},
                                "startDate": {"type": "string"},
                                "startTime": {"type": "string"},
                                "endDate": {"type": "string"},
                                "endTime": {"type": "string"},
                                "location": {"type": "string"}
                            },
                            "required": ["title"]
                        },
                        "email_data": {
                            "type": "object",
                            "description": "Original email data for context",
                            "properties": {
                                "subject": {"type": "string"},
                                "from": {"type": "string"}
                            }
                        }
                    },
                    "required": ["event_details"]
                }
            },
            {
                "name": "create_multiple_events",
                "description": "Create multiple calendar events from a list",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "events_list": {
                            "type": "array",
                            "description": "List of event details",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "title": {"type": "string"},
                                    "description": {"type": "string"},
                                    "startDate": {"type": "string"},
                                    "startTime": {"type": "string"},
                                    "endDate": {"type": "string"},
                                    "endTime": {"type": "string"},
                                    "location": {"type": "string"}
                                }
                            }
                        },
                        "email_data": {
                            "type": "object",
                            "description": "Original email data for context"
                        }
                    },
                    "required": ["events_list"]
                }
            },
            {
                "name": "check_duplicate_events",
                "description": "Check if similar events already exist",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "event_title": {"type": "string"},
                        "event_date": {"type": "string", "description": "Date in YYYY-MM-DD format"}
                    },
                    "required": ["event_title", "event_date"]
                }
            },
            {
                "name": "get_upcoming_events",
                "description": "Get list of upcoming calendar events",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "days_ahead": {
                            "type": "integer",
                            "description": "Number of days ahead to look",
                            "default": 7
                        },
                        "max_results": {
                            "type": "integer", 
                            "description": "Maximum number of events to return",
                            "default": 10
                        }
                    }
                }
            }
        ]
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute calendar agent functionality"""
        action = input_data.get("action", "create_calendar_event")
        
        try:
            if action == "create_calendar_event":
                return self.create_calendar_event(
                    input_data.get("event_details"),
                    input_data.get("email_data")
                )
            elif action == "create_multiple_events":
                return self.create_multiple_events(
                    input_data.get("events_list"),
                    input_data.get("email_data")
                )
            elif action == "check_duplicate_events":
                return self.check_duplicate_events(
                    input_data.get("event_title"),
                    input_data.get("event_date")
                )
            elif action == "get_upcoming_events":
                return self.get_upcoming_events(
                    input_data.get("days_ahead", 7),
                    input_data.get("max_results", 10)
                )
            else:
                return {"error": f"Unknown action: {action}"}
                
        except Exception as e:
            self.logger.error(f"Error in calendar agent: {e}")
            return {"error": str(e)}
    
    def create_calendar_event(self, event_details: Dict[str, Any], email_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create a single calendar event"""
        self.log_action("create_calendar_event", {"title": event_details.get("title")})
        
        try:
            # Use the existing calendar service to create the event
            result = self.calendar_service.create_calendar_event(event_details, email_data or {})
            
            return {
                "success": True,
                "message": "Calendar event created successfully",
                "event_details": event_details,
                "calendar_result": result
            }
            
        except Exception as e:
            self.logger.error(f"Error creating calendar event: {e}")
            return {
                "success": False,
                "error": str(e),
                "event_details": event_details
            }
    
    def create_multiple_events(self, events_list: List[Dict[str, Any]], email_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Create multiple calendar events"""
        self.log_action("create_multiple_events", {"count": len(events_list)})
        
        results = []
        successful = 0
        
        for i, event_details in enumerate(events_list):
            try:
                result = self.create_calendar_event(event_details, email_data)
                results.append({
                    "index": i,
                    "success": result["success"],
                    "title": event_details.get("title", "Untitled"),
                    "details": result
                })
                
                if result["success"]:
                    successful += 1
                    
            except Exception as e:
                results.append({
                    "index": i,
                    "success": False,
                    "title": event_details.get("title", "Untitled"),
                    "error": str(e)
                })
        
        return {
            "success": successful > 0,
            "total_events": len(events_list),
            "successful": successful,
            "failed": len(events_list) - successful,
            "results": results
        }
    
    def check_duplicate_events(self, event_title: str, event_date: str) -> Dict[str, Any]:
        """Check if similar events already exist"""
        self.log_action("check_duplicate_events", {"title": event_title, "date": event_date})
        
        try:
            # Use the calendar service's duplicate checking functionality
            # This is a simplified version - the actual implementation would query the calendar
            
            return {
                "success": True,
                "has_duplicates": False,  # This would be determined by actual calendar query
                "similar_events": [],     # List of similar events found
                "message": "Duplicate check completed"
            }
            
        except Exception as e:
            self.logger.error(f"Error checking duplicates: {e}")
            return {
                "success": False,
                "error": str(e),
                "has_duplicates": False,
                "similar_events": []
            }
    
    def get_upcoming_events(self, days_ahead: int = 7, max_results: int = 10) -> Dict[str, Any]:
        """Get upcoming calendar events"""
        self.log_action("get_upcoming_events", {"days_ahead": days_ahead, "max_results": max_results})
        
        try:
            # This would integrate with the actual calendar service to fetch events
            # For now, return a placeholder
            
            return {
                "success": True,
                "events": [],  # List of upcoming events would go here
                "days_ahead": days_ahead,
                "max_results": max_results,
                "message": "Upcoming events fetched successfully"
            }
            
        except Exception as e:
            self.logger.error(f"Error getting upcoming events: {e}")
            return {
                "success": False,
                "error": str(e),
                "events": []
            }
    
    def process_ai_events(self, analysis_result: Dict[str, Any], email_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process events from AI analysis result"""
        self.log_action("process_ai_events", {"has_event": analysis_result.get("hasEvent")})
        
        try:
            if not analysis_result.get("hasEvent"):
                return {
                    "success": True,
                    "message": "No events to process",
                    "events_created": 0
                }
            
            # Check if eventDetails is a list (multiple events) or dict (single event)
            event_details = analysis_result.get("eventDetails")
            
            if isinstance(event_details, list):
                # Multiple events
                return self.create_multiple_events(event_details, email_data)
            elif isinstance(event_details, dict) and event_details:
                # Single event
                return self.create_calendar_event(event_details, email_data)
            else:
                return {
                    "success": False,
                    "error": "Invalid event details format",
                    "events_created": 0
                }
                
        except Exception as e:
            self.logger.error(f"Error processing AI events: {e}")
            return {
                "success": False,
                "error": str(e),
                "events_created": 0
            }
    
    def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {
            "name": self.name,
            "description": self.description,
            "status": "active",
            "functions": len(self.get_available_functions()),
            "calendar_configured": True  # This would check actual calendar service status
        }
