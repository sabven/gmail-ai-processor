"""AI processing service for email analysis"""

import json
import logging
import openai
from typing import Dict

logger = logging.getLogger(__name__)

class AIService:
    """Service for processing emails with AI"""
    
    def __init__(self, config):
        self.config = config
        self._setup_clients()
    
    def _setup_clients(self):
        """Initialize OpenAI client"""
        self.openai_client = None
        
        # OpenAI client
        if self.config.OPENAI_API_KEY:
            from openai import OpenAI
            self.openai_client = OpenAI(api_key=self.config.OPENAI_API_KEY)
        else:
            logger.warning("No OpenAI API key provided. AI processing will not work.")
    
    def process_email_with_ai(self, email_data: Dict) -> Dict:
        """Process email using AI Agent (OpenAI) with enhanced GPT-5 prompting"""
        
        # Enhanced prompt for better AI processing (optimized for GPT-5)
        prompt = f"""
        You are an expert email processing assistant specializing in school communications for parents.
        
        Analyze this school email with focus on what actions parents need to take:

        EMAIL DETAILS:
        Subject: {email_data['subject']}
        From: {email_data['from']}
        Content: {email_data['body']}

        ANALYSIS REQUIREMENTS:
        1. Create a concise, informative summary (max 100 words)
        2. Identify ALL dates, times, events, meetings, deadlines, or appointments
        3. Extract location information if mentioned
        4. Determine priority level based on urgency and importance
        5. Generate 2-3 SPECIFIC action items for parents (e.g., "Sign permission slip by Friday", "Pack swimming gear for tomorrow", "Submit medical form online")

        PARENT ACTION FOCUS:
        - What does the parent need to DO?
        - What needs to be prepared/purchased/signed?
        - What deadlines must be met?
        - What responses are required?
        - What items need to be sent to school?

        RESPONSE FORMAT (JSON only):
        {{
          "gist": "Clear, concise summary highlighting key information",
          "hasEvent": true/false,
          "eventDetails": {{
            "title": "Specific event title",
            "description": "Detailed event description", 
            "startDate": "YYYY-MM-DD",
            "startTime": "HH:MM (or 'Unknown' if not specified)",
            "endDate": "YYYY-MM-DD",
            "endTime": "HH:MM (or 'Unknown' if not specified)",
            "location": "Specific location or 'Unknown'"
          }},
          "priority": "high/medium/low",
          "actionItems": ["Specific parent action 1", "Specific parent action 2", "Specific parent action 3"],
          "category": "academic/administrative/social/sports/health/other"
        }}

        Note: For multiple events in one email, create separate entries or combine logically.
        Make action items specific, practical and time-bound where possible.
        """
        
        try:
            # Use OpenAI for all AI processing
            ai_response = self._call_openai(prompt)
            
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
        """Call OpenAI API with model fallback support"""
        try:
            # List of models to try in order of preference
            models_to_try = []
            
            # Add the configured model first
            if self.config.AI_MODEL:
                models_to_try.append(self.config.AI_MODEL)
            
            # Add fallback models
            fallback_models = ['gpt-4o', 'gpt-4o-mini', 'gpt-4-turbo', 'gpt-4', 'gpt-3.5-turbo']
            for model in fallback_models:
                if model not in models_to_try:
                    models_to_try.append(model)
            
            last_error = None
            for model in models_to_try:
                try:
                    logger.info(f"Attempting to use OpenAI model: {model}")
                    
                    # Prepare API parameters - handle different parameter formats
                    api_params = {
                        "model": model,
                        "messages": [
                            {"role": "system", "content": "You are an expert email processing assistant with advanced analytical capabilities. Always respond with valid, well-structured JSON. Focus on accuracy, detail extraction, and practical insights."},
                            {"role": "user", "content": prompt}
                        ]
                    }
                    
                    # Handle different model parameter requirements
                    if model.startswith('gpt-5'):
                        # GPT-5 specific parameters
                        api_params["max_completion_tokens"] = 800
                        # GPT-5 might only support default temperature
                    elif model in ['gpt-4o', 'gpt-4o-mini']:
                        api_params["max_completion_tokens"] = 800
                        api_params["temperature"] = 0.3
                    else:
                        # Older models
                        api_params["max_tokens"] = 800
                        api_params["temperature"] = 0.3
                    
                    response = self.openai_client.chat.completions.create(**api_params)
                    logger.info(f"Successfully used OpenAI model: {model}")
                    
                    # Get the content and log it for debugging
                    content = response.choices[0].message.content
                    if not content or content.strip() == "":
                        logger.warning(f"Model {model} returned empty response, trying next...")
                        continue
                    
                    logger.debug(f"Model {model} response: {content[:200]}...")
                    return content
                
                except Exception as e:
                    last_error = e
                    if "model_not_found" in str(e).lower() or "does not exist" in str(e).lower():
                        logger.warning(f"Model {model} not available, trying next fallback...")
                        continue
                    else:
                        # For other errors, don't continue trying other models
                        raise e
            
            # If we get here, all models failed
            raise Exception(f"All OpenAI models failed. Last error: {last_error}")
        
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise e
    
    def _parse_ai_response(self, ai_response: str, email_data: Dict) -> Dict:
        """Parse AI response into structured format"""
        try:
            if not ai_response or ai_response.strip() == "":
                logger.warning("Empty AI response received")
                return self._create_fallback_response(email_data)
            
            # Extract JSON from response
            start_idx = ai_response.find('{')
            end_idx = ai_response.rfind('}') + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = ai_response[start_idx:end_idx]
                parsed_response = json.loads(json_str)
                
                # Validate required fields
                if not parsed_response.get('gist'):
                    parsed_response['gist'] = self._extract_summary_from_email(email_data)
                
                return parsed_response
            else:
                logger.warning("No JSON found in AI response")
                return self._create_fallback_response(email_data, ai_response)
            
        except json.JSONDecodeError as e:
            logger.warning(f"JSON parsing failed: {e}")
            return self._create_fallback_response(email_data, ai_response)
    
    def _create_fallback_response(self, email_data: Dict, ai_response: str = None) -> Dict:
        """Create a fallback response when AI processing fails"""
        summary = ai_response[:200] + "..." if ai_response and len(ai_response) > 200 else (ai_response or self._extract_summary_from_email(email_data))
        
        return {
            "gist": summary,
            "hasEvent": False,
            "eventDetails": {},
            "priority": "medium",
            "actionItems": [],
            "category": "other"
        }
    
    def _extract_summary_from_email(self, email_data: Dict) -> str:
        """Extract a basic summary from email data when AI fails"""
        subject = email_data.get('subject', 'No subject')
        sender = email_data.get('from', 'Unknown sender')
        body = email_data.get('body', '')
        
        # Create a simple summary
        if len(body) > 100:
            body_preview = body[:100] + "..."
        else:
            body_preview = body
        
        return f"Email from {sender} about '{subject}': {body_preview}"
