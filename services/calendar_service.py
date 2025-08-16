"""Google Calendar service"""

import os
import logging
from typing import Dict
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

logger = logging.getLogger(__name__)

class CalendarService:
    """Service for Google Calendar integration"""
    
    def __init__(self, config):
        self.config = config
        self.calendar_service = self._setup_google_calendar()
    
    def _setup_google_calendar(self):
        """Setup Google Calendar API client"""
        try:
            # Skip calendar setup in cloud environments (no browser available)
            is_cloud_environment = os.getenv('GITHUB_ACTIONS') == 'true' or os.getenv('CI') == 'true'
            if is_cloud_environment:
                logger.info("Skipping Google Calendar setup in cloud environment - no browser available")
                logger.info("Google Calendar service will be disabled. Email processing will continue without calendar integration.")
                return None
                
            creds = None
            
            # Load existing token
            if os.path.exists(self.config.GOOGLE_CALENDAR_TOKEN_FILE):
                try:
                    creds = Credentials.from_authorized_user_file(
                        self.config.GOOGLE_CALENDAR_TOKEN_FILE, 
                        self.config.CALENDAR_SCOPES
                    )
                except Exception as e:
                    logger.warning(f"Failed to load existing token: {e}")
                    # Remove corrupted token file
                    os.remove(self.config.GOOGLE_CALENDAR_TOKEN_FILE)
                    creds = None
            
            # If no valid credentials, get new ones
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    try:
                        creds.refresh(Request())
                    except Exception as e:
                        logger.warning(f"Failed to refresh token: {e}")
                        # Remove expired token and try to get new credentials
                        if os.path.exists(self.config.GOOGLE_CALENDAR_TOKEN_FILE):
                            os.remove(self.config.GOOGLE_CALENDAR_TOKEN_FILE)
                        creds = None
                
                # Get new credentials if needed
                if not creds:
                    if not os.path.exists(self.config.GOOGLE_CALENDAR_CREDENTIALS_FILE):
                        logger.warning(f"Google Calendar credentials file not found: {self.config.GOOGLE_CALENDAR_CREDENTIALS_FILE}")
                        logger.info("To enable Google Calendar:")
                        logger.info("1. Go to https://console.cloud.google.com/")
                        logger.info("2. Enable Calendar API")
                        logger.info("3. Download credentials.json to this directory")
                        return None
                    
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.config.GOOGLE_CALENDAR_CREDENTIALS_FILE, 
                        self.config.CALENDAR_SCOPES
                    )
                    creds = flow.run_local_server(port=0)
                
                # Save credentials for next run
                with open(self.config.GOOGLE_CALENDAR_TOKEN_FILE, 'w') as token:
                    token.write(creds.to_json())
            
            service = build('calendar', 'v3', credentials=creds)
            logger.info("Google Calendar service initialized successfully")
            return service
        
        except Exception as e:
            logger.warning(f"Could not setup Google Calendar: {e}")
            logger.info("Google Calendar service will be disabled. Email processing will continue without calendar integration.")
            return None
    
    def create_calendar_event(self, event_details, email_data: Dict) -> bool:
        """Create Google Calendar event(s) - handles both single events and lists of events"""
        
        try:
            if not self.calendar_service:
                logger.error("Google Calendar service not available")
                return False
            
            # Log the event details for debugging
            logger.info(f"Creating calendar event with details: {event_details}")
            
            # Handle both single event (dict) and multiple events (list)
            if isinstance(event_details, list):
                # Multiple events
                success_count = 0
                for event in event_details:
                    if self._create_single_event(event, email_data):
                        success_count += 1
                logger.info(f"Created {success_count} out of {len(event_details)} calendar events")
                return success_count > 0
            else:
                # Single event
                return self._create_single_event(event_details, email_data)
            
        except Exception as e:
            logger.error(f"Error creating calendar event: {e}")
            return False

    def _create_single_event(self, event_details: Dict, email_data: Dict) -> bool:
        """Create a single calendar event"""
        try:
            # Check if event already exists
            event_title = event_details.get('title', 'Event from Email')
            event_date = event_details.get('startDate', '')
            
            if self._event_exists(event_title, event_date):
                logger.info(f"Event '{event_title}' on {event_date} already exists, skipping creation")
                return True  # Return True since the event exists (no need to create)
            
            # Handle missing or invalid times - default to 7 AM - 8 AM
            start_time = event_details.get('startTime', '07:00')
            end_time = event_details.get('endTime', '08:00')
            
            # Clean up invalid time values
            if not start_time or start_time in ['Unknown', '', 'unknown', 'N/A', 'NA']:
                start_time = '07:00'
            if not end_time or end_time in ['Unknown', '', 'unknown', 'N/A', 'NA']:
                end_time = '08:00'
            
            # Ensure proper time format (HH:MM)
            if len(start_time.split(':')) != 2:
                start_time = '07:00'
            if len(end_time.split(':')) != 2:
                end_time = '08:00'
            
            # Prepare event data
            start_datetime = f"{event_details.get('startDate', '')}T{start_time}:00"
            end_datetime = f"{event_details.get('endDate', event_details.get('startDate', ''))}T{end_time}:00"
            
            logger.info(f"Event datetime: {start_datetime} to {end_datetime}")
            
            event = {
                'summary': event_details.get('title', 'Event from Email'),
                'description': f"{event_details.get('description', '')}\n\nSource Email: {email_data['subject']}\nFrom: {email_data['from']}",
                'start': {
                    'dateTime': start_datetime,
                    'timeZone': 'Asia/Singapore',
                },
                'end': {
                    'dateTime': end_datetime,
                    'timeZone': 'Asia/Singapore',
                },
                'location': event_details.get('location', ''),
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 24 * 60},
                        {'method': 'popup', 'minutes': 10},
                    ],
                },
            }
            
            # Create the event
            created_event = self.calendar_service.events().insert(
                calendarId='primary', 
                body=event
            ).execute()
            
            logger.info(f"Calendar event created: {created_event.get('htmlLink')}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating single calendar event: {e}")
            return False

    def _event_exists(self, event_title: str, event_date: str) -> bool:
        """Check if an event with the same title and date already exists"""
        try:
            if not event_date:
                return False
            
            # Search for events on the specified date
            time_min = f"{event_date}T00:00:00Z"
            time_max = f"{event_date}T23:59:59Z"
            
            events_result = self.calendar_service.events().list(
                calendarId='primary',
                timeMin=time_min,
                timeMax=time_max,
                maxResults=250,  # Check up to 250 events for that day
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            # Check if any event has the same or very similar title
            for event in events:
                existing_title = event.get('summary', '').strip().lower()
                search_title = event_title.strip().lower()
                
                # Exact match
                if existing_title == search_title:
                    logger.info(f"Found existing event with exact title '{event_title}' on {event_date}")
                    return True
                
                # Check for similar titles (contains or very close match)
                if len(search_title) > 10:  # Only for longer titles
                    if search_title in existing_title or existing_title in search_title:
                        logger.info(f"Found existing event with similar title '{existing_title}' vs '{event_title}' on {event_date}")
                        return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking for existing events: {e}")
            return False  # If we can't check, assume it doesn't exist and try to create
