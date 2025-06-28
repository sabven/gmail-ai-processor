"""Analysis Agent - Handles AI-powered email analysis"""

import json
import logging
from typing import Any, Dict, List

from agents.base_agent import BaseAgentClass
from openai import OpenAI
from anthropic import Anthropic

logger = logging.getLogger(__name__)

class AnalysisAgent(BaseAgentClass):
    """Agent responsible for AI-powered email analysis"""
    
    def __init__(self, config):
        super().__init__(config)
        self.name = "analysis_agent"
        self.description = "Analyzes emails using AI to extract insights and event information"
        self._setup_ai_clients()
    
    def _setup_ai_clients(self):
        """Initialize AI clients"""
        # OpenAI client
        if self.config.OPENAI_API_KEY:
            self.openai_client = OpenAI(api_key=self.config.OPENAI_API_KEY)
        
        # Anthropic client
        if self.config.ANTHROPIC_API_KEY:
            self.anthropic_client = Anthropic(api_key=self.config.ANTHROPIC_API_KEY)
    
    def get_available_functions(self) -> List[Dict[str, Any]]:
        """Return available analysis functions"""
        return [
            {
                "name": "analyze_email",
                "description": "Analyze an email to extract summary, events, and insights",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "email_data": {
                            "type": "object",
                            "description": "Email data containing subject, body, from, etc.",
                            "properties": {
                                "subject": {"type": "string"},
                                "body": {"type": "string"},
                                "from": {"type": "string"}
                            },
                            "required": ["subject", "body", "from"]
                        },
                        "analysis_type": {
                            "type": "string",
                            "description": "Type of analysis to perform",
                            "enum": ["summary", "events", "full"],
                            "default": "full"
                        }
                    },
                    "required": ["email_data"]
                }
            },
            {
                "name": "extract_events",
                "description": "Extract calendar events from email content",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "email_content": {
                            "type": "string",
                            "description": "The email content to analyze for events"
                        }
                    },
                    "required": ["email_content"]
                }
            }
        ]
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute analysis agent functionality"""
        action = input_data.get("action", "analyze_email")
        
        try:
            if action == "analyze_email":
                return self.analyze_email(
                    input_data.get("email_data"),
                    input_data.get("analysis_type", "full")
                )
            elif action == "extract_events":
                return self.extract_events(input_data.get("email_content"))
            else:
                return {"error": f"Unknown action: {action}"}
                
        except Exception as e:
            self.logger.error(f"Error in analysis agent: {e}")
            return {"error": str(e)}
    
    def analyze_email(self, email_data: Dict[str, Any], analysis_type: str = "full") -> Dict[str, Any]:
        """Analyze email content using AI"""
        self.log_action("analyze_email", {"subject": email_data.get("subject"), "type": analysis_type})
        
        try:
            # Create analysis prompt based on type
            if analysis_type == "summary":
                prompt = self._create_summary_prompt(email_data)
            elif analysis_type == "events":
                prompt = self._create_events_prompt(email_data)
            else:  # full analysis
                prompt = self._create_full_analysis_prompt(email_data)
            
            # Get AI response
            if self.config.AI_MODEL.startswith('gpt'):
                ai_response = self._call_openai(prompt)
            else:
                ai_response = self._call_anthropic(prompt)
            
            # Parse and return results
            result = self._parse_ai_response(ai_response, email_data)
            result["success"] = True
            return result
            
        except Exception as e:
            self.logger.error(f"Error analyzing email: {e}")
            return {
                "success": False,
                "error": str(e),
                "gist": f"Error analyzing email: {email_data.get('subject', 'Unknown')}",
                "hasEvent": False,
                "eventDetails": {}
            }
    
    def extract_events(self, email_content: str) -> Dict[str, Any]:
        """Extract events specifically from email content"""
        self.log_action("extract_events", {"content_length": len(email_content)})
        
        try:
            prompt = f"""
            Extract any events, meetings, deadlines, or appointments from this email content.
            
            Email Content: {email_content}
            
            Respond with JSON containing events found:
            {{
              "events_found": true/false,
              "events": [
                {{
                  "title": "Event title",
                  "description": "Event description",
                  "startDate": "YYYY-MM-DD",
                  "startTime": "HH:MM",
                  "endDate": "YYYY-MM-DD",
                  "endTime": "HH:MM",
                  "location": "Location if mentioned"
                }}
              ]
            }}
            """
            
            # Get AI response
            if self.config.AI_MODEL.startswith('gpt'):
                ai_response = self._call_openai(prompt)
            else:
                ai_response = self._call_anthropic(prompt)
            
            # Parse response
            try:
                start_idx = ai_response.find('{')
                end_idx = ai_response.rfind('}') + 1
                json_str = ai_response[start_idx:end_idx]
                result = json.loads(json_str)
                result["success"] = True
                return result
            except json.JSONDecodeError:
                return {
                    "success": False,
                    "error": "Could not parse AI response",
                    "events_found": False,
                    "events": []
                }
                
        except Exception as e:
            self.logger.error(f"Error extracting events: {e}")
            return {
                "success": False,
                "error": str(e),
                "events_found": False,
                "events": []
            }
    
    def _create_full_analysis_prompt(self, email_data: Dict[str, Any]) -> str:
        """Create prompt for full email analysis"""
        return f"""
        Please analyze this email and provide:
        1. A brief gist/summary (max 100 words)
        2. Identify if there are any events, meetings, deadlines, or appointments mentioned that should be added to calendar
        3. Extract any actionable items or important information

        Email Subject: {email_data['subject']}
        From: {email_data['from']}
        Content: {email_data['body']}

        Please respond in this JSON format:
        {{
          "gist": "Brief summary here",
          "hasEvent": true/false,
          "eventDetails": {{
            "title": "Event title",
            "description": "Event description", 
            "startDate": "YYYY-MM-DD",
            "startTime": "HH:MM",
            "endDate": "YYYY-MM-DD",
            "endTime": "HH:MM",
            "location": "Location if mentioned"
          }},
          "actionItems": ["List of action items"],
          "priority": "high/medium/low",
          "sentiment": "positive/neutral/negative"
        }}
        """
    
    def _create_summary_prompt(self, email_data: Dict[str, Any]) -> str:
        """Create prompt for email summary only"""
        return f"""
        Provide a brief summary of this email (max 100 words):
        
        Subject: {email_data['subject']}
        From: {email_data['from']}
        Content: {email_data['body']}
        
        Respond in JSON format:
        {{
          "gist": "Brief summary here"
        }}
        """
    
    def _create_events_prompt(self, email_data: Dict[str, Any]) -> str:
        """Create prompt for event extraction only"""
        return f"""
        Extract any events, meetings, or appointments from this email:
        
        Subject: {email_data['subject']}
        Content: {email_data['body']}
        
        Respond in JSON format:
        {{
          "hasEvent": true/false,
          "eventDetails": {{
            "title": "Event title",
            "description": "Event description",
            "startDate": "YYYY-MM-DD", 
            "startTime": "HH:MM",
            "endDate": "YYYY-MM-DD",
            "endTime": "HH:MM",
            "location": "Location if mentioned"
          }}
        }}
        """
    
    def _call_openai(self, prompt: str) -> str:
        """Call OpenAI API"""
        response = self.openai_client.chat.completions.create(
            model=self.config.AI_MODEL,
            messages=[
                {"role": "system", "content": "You are an expert email processing assistant. Always respond with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=500
        )
        return response.choices[0].message.content
    
    def _call_anthropic(self, prompt: str) -> str:
        """Call Anthropic API"""
        message = self.anthropic_client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=500,
            temperature=0.3,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text
    
    def _parse_ai_response(self, ai_response: str, email_data: Dict) -> Dict:
        """Parse AI response into structured format"""
        try:
            # Extract JSON from response
            start_idx = ai_response.find('{')
            end_idx = ai_response.rfind('}') + 1
            json_str = ai_response[start_idx:end_idx]
            return json.loads(json_str)
            
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            return {
                "gist": ai_response[:200] + "..." if len(ai_response) > 200 else ai_response,
                "hasEvent": False,
                "eventDetails": {}
            }
    
    def get_status(self) -> Dict[str, Any]:
        """Get agent status"""
        return {
            "name": self.name,
            "description": self.description,
            "status": "active",
            "ai_model": self.config.AI_MODEL,
            "functions": len(self.get_available_functions())
        }
