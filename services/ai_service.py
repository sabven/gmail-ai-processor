"""AI processing service for email analysis"""

import json
import logging
import openai
from anthropic import Anthropic
from typing import Dict

logger = logging.getLogger(__name__)

class AIService:
    """Service for processing emails with AI"""
    
    def __init__(self, config):
        self.config = config
        self._setup_clients()
    
    def _setup_clients(self):
        """Initialize AI clients"""
        # OpenAI client
        if self.config.OPENAI_API_KEY:
            from openai import OpenAI
            self.openai_client = OpenAI(api_key=self.config.OPENAI_API_KEY)
        
        # Anthropic client
        if self.config.ANTHROPIC_API_KEY:
            self.anthropic_client = Anthropic(api_key=self.config.ANTHROPIC_API_KEY)
    
    def process_email_with_ai(self, email_data: Dict) -> Dict:
        """Process email using AI Agent (OpenAI or Anthropic)"""
        
        prompt = f"""
        Please analyze this email and provide:
        1. A brief gist/summary (max 100 words)
        2. Identify if there are any events, meetings, deadlines, or appointments mentioned that should be added to calendar

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
          }}
        }}
        """
        
        try:
            if self.config.AI_MODEL.startswith('gpt'):
                ai_response = self._call_openai(prompt)
            else:
                ai_response = self._call_anthropic(prompt)
            
            # Parse JSON response
            return self._parse_ai_response(ai_response, email_data)
            
        except Exception as e:
            logger.error(f"Error processing email with AI: {e}")
            return {
                "gist": f"Error processing email: {email_data['subject']}",
                "hasEvent": False,
                "eventDetails": {}
            }
    
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
