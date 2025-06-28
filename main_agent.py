#!/usr/bin/env python3
"""
Gmail AI Agent Processor - Agent-based Architecture
Processes emails using specialized AI agents for analysis, notifications, and calendar management
"""

import os
import sys
import logging
import argparse
import schedule
import time
from datetime import datetime

from config import Config
from agent_email_processor import AgentEmailProcessor
from email_processor import EmailProcessor  # Legacy processor

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('email_processor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def create_env_file():
    """Create a sample .env file with all required variables"""
    env_content = """# Gmail IMAP Configuration
GMAIL_USER=your_email@gmail.com
GMAIL_APP_PASSWORD=your_app_password  # Generate this in Gmail settings

# AI/LLM Configuration (choose one)
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
AI_MODEL=gpt-3.5-turbo  # or gpt-4, claude-3-sonnet-20240229

# WhatsApp via Twilio (Option 1)
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
YOUR_WHATSAPP_NUMBER=whatsapp:+65123456789

# WhatsApp via CallMeBot (Option 2 - Simpler)
WHATSAPP_API_KEY=your_callmebot_api_key
WHATSAPP_PHONE=65123456789

# Google Calendar (download credentials.json from Google Cloud Console)
# Place credentials.json in the same directory as this script
"""
    
    with open('.env.example', 'w') as f:
        f.write(env_content)
    
    print("Created .env.example file. Please copy it to .env and fill in your credentials.")

def validate_config(config):
    """Validate the configuration"""
    errors = []
    
    if not config.GMAIL_USER or not config.GMAIL_PASSWORD:
        errors.append("Gmail credentials not configured")
    
    if not config.OPENAI_API_KEY and not config.ANTHROPIC_API_KEY:
        errors.append("No AI API key configured")
    
    # Check WhatsApp configuration (either Twilio or CallMeBot)
    twilio_configured = config.TWILIO_ACCOUNT_SID and config.TWILIO_AUTH_TOKEN and config.YOUR_WHATSAPP_NUMBER
    callmebot_configured = config.CALLMEBOT_API_KEY and config.CALLMEBOT_PHONE
    
    if not twilio_configured and not callmebot_configured:
        errors.append("Neither Twilio nor CallMeBot WhatsApp credentials are configured")
    
    return errors

def run_agent_processor(config, max_emails=10):
    """Run the agent-based email processor"""
    logger.info("🤖 Starting Agent-based Email Processing...")
    
    try:
        processor = AgentEmailProcessor(config)
        
        # Run health check first
        logger.info("Running health check...")
        health_result = processor.run_health_check()
        
        if health_result.get("success"):
            logger.info(f"Health check: {health_result.get('overall_health', 'unknown')}")
            if health_result.get("overall_health") == "unhealthy":
                logger.warning("System health is poor, but continuing...")
        
        # Process emails
        result = processor.process_emails(max_emails)
        
        if result.get("success"):
            logger.info(f"✅ Agent processing completed: {result.get('message')}")
            if result.get("stats"):
                stats = result["stats"]
                logger.info(f"📊 Stats - Emails: {stats.get('emails_processed', 0)}, "
                          f"Events: {stats.get('events_created', 0)}, "
                          f"Notifications: {stats.get('notifications_sent', 0)}, "
                          f"Errors: {stats.get('errors', 0)}")
        else:
            logger.error(f"❌ Agent processing failed: {result.get('error')}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error in agent processor: {e}")
        return {"success": False, "error": str(e)}

def run_legacy_processor(config):
    """Run the legacy email processor"""
    logger.info("🔧 Starting Legacy Email Processing...")
    
    try:
        processor = EmailProcessor(config)
        processor.process_emails()
        logger.info("✅ Legacy processing completed")
        return {"success": True, "message": "Legacy processing completed"}
        
    except Exception as e:
        logger.error(f"Error in legacy processor: {e}")
        return {"success": False, "error": str(e)}

def show_agent_info(config):
    """Show information about available agents and their functions"""
    try:
        processor = AgentEmailProcessor(config)
        info = processor.get_agent_info()
        
        if info.get("success"):
            print("\n🤖 Agent-based Email Processing System")
            print("=" * 50)
            
            # Coordinator info
            coordinator = info["coordinator"]
            print(f"\n📋 Coordinator: {coordinator['name']}")
            print(f"   Description: {coordinator['description']}")
            print(f"   Functions: {len(coordinator['functions'])}")
            
            # Agent info
            print("\n🔧 Specialized Agents:")
            for agent_key, agent_info in info["agents"].items():
                print(f"   • {agent_info['name']}")
                print(f"     {agent_info['description']}")
                print(f"     Functions available: {len(agent_info['functions'])}")
            
            print(f"\n⏰ Generated: {info['timestamp']}")
            
        else:
            print(f"Error getting agent info: {info.get('error')}")
            
    except Exception as e:
        print(f"Error showing agent info: {e}")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Gmail AI Agent Processor')
    parser.add_argument('--mode', choices=['agent', 'legacy', 'info', 'health'], 
                       default='agent', help='Processing mode')
    parser.add_argument('--max-emails', type=int, default=10, 
                       help='Maximum number of emails to process')
    parser.add_argument('--schedule', action='store_true', 
                       help='Run on schedule (daily at 5 PM)')
    parser.add_argument('--create-env', action='store_true',
                       help='Create example .env file')
    
    args = parser.parse_args()
    
    # Handle create-env option
    if args.create_env:
        create_env_file()
        return
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("No .env file found. Creating example...")
        create_env_file()
        print("Please configure the .env file and run again.")
        return
    
    # Initialize configuration
    try:
        config = Config()
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        return
    
    # Validate configuration
    config_errors = validate_config(config)
    if config_errors:
        logger.error("Configuration errors:")
        for error in config_errors:
            logger.error(f"  - {error}")
        logger.info("Please check your .env file configuration")
        return
    
    # Handle different modes
    if args.mode == 'info':
        show_agent_info(config)
        return
    
    if args.mode == 'health':
        logger.info("Running health check...")
        processor = AgentEmailProcessor(config)
        result = processor.run_health_check()
        
        if result.get("success"):
            print(f"\n🏥 System Health Check")
            print("=" * 30)
            print(f"Overall Health: {result.get('overall_health', 'unknown').upper()}")
            print(f"Healthy Services: {result.get('healthy_services', 0)}/{result.get('total_services', 0)}")
            
            print("\n📋 Service Details:")
            for service, health in result.get("service_health", {}).items():
                status_emoji = "✅" if health["status"] == "healthy" else "❌"
                print(f"   {status_emoji} {service}: {health['status']} - {health['details']}")
        else:
            print(f"Health check failed: {result.get('error')}")
        return
    
    # Define processing function based on mode
    if args.mode == 'agent':
        process_function = lambda: run_agent_processor(config, args.max_emails)
    else:  # legacy
        process_function = lambda: run_legacy_processor(config)
    
    # Handle scheduling
    if args.schedule:
        logger.info(f"Scheduling {args.mode} processing to run daily at 5 PM...")
        schedule.every().day.at("17:00").do(process_function)
        
        logger.info("Email processor started. Scheduled to run daily at 5 PM.")
        logger.info("Press Ctrl+C to stop.")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            logger.info("Email processor stopped.")
    else:
        # Run immediately
        logger.info(f"Running {args.mode} processing immediately...")
        result = process_function()
        
        if result.get("success"):
            logger.info("Processing completed successfully!")
        else:
            logger.error(f"Processing failed: {result.get('error')}")

if __name__ == "__main__":
    main()
