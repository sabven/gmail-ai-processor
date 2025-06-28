# Gmail AI Email Processor

This application processes emails from Gmail, analyzes them with AI, sends WhatsApp notifications, and creates calendar events automatically.

## Features

- **Email Processing**: Fetches emails from Gmail using IMAP
- **AI Analysis**: Uses OpenAI GPT or Anthropic Claude to analyze email content
- **WhatsApp Notifications**: Sends summaries via Twilio or CallMeBot
- **Calendar Integration**: Creates Google Calendar events for meetings/appointments
- **Scheduled Execution**: Runs daily at 5 PM automatically

## Setup Instructions

### 1. Install Dependencies

**Option A: Using UV (Recommended - 10x faster)**
```bash
# Install UV first
pip install uv

# Install dependencies with UV
uv sync
```

**Option B: Using pip (Traditional)**
```bash
pip install -r requirements.txt
```

### 2. Configuration

1. Copy `.env.example` to `.env`:
   ```bash
   copy .env.example .env
   ```

2. Fill in your credentials in the `.env` file:

#### Gmail Setup
- Enable 2-factor authentication
- Generate an App Password: Google Account → Security → App passwords
- Use your email and app password in the `.env` file

#### AI Service (Choose one)
- **OpenAI**: Get API key from https://platform.openai.com/
- **Anthropic**: Get API key from https://console.anthropic.com/

#### WhatsApp Service (Choose one)

**Option 1: Twilio (Recommended)**
- Sign up at https://www.twilio.com/
- Get Account SID and Auth Token
- Enable WhatsApp sandbox

**Option 2: CallMeBot (Simpler)**
- Add CallMeBot to WhatsApp: https://www.callmebot.com/blog/free-api-whatsapp-messages/
- Get your API key

#### Google Calendar
- Go to Google Cloud Console
- Enable Calendar API
- Download `credentials.json` and place in project root

### 3. Run the Application

**Using UV (Recommended):**
```bash
# Run the application
uv run python main.py

# Install dependencies (if needed)
uv sync

# Install dev dependencies
uv sync --extra dev

# Run tests (if available)
uv run pytest
```

**Using traditional Python:**
```bash
python main.py
```

## UV Package Manager

This project is configured to use [UV](https://docs.astral.sh/uv/), a modern Python package manager. UV provides:

- **Fast dependency resolution**: Much faster than pip
- **Reliable builds**: Lockfile ensures reproducible environments  
- **Modern workflow**: Built-in virtual environment management
- **Better caching**: Faster subsequent installs

### UV Installation

Install UV using one of these methods:

**Windows (PowerShell):**
```powershell
irm https://astral.sh/uv/install.ps1 | iex
```

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### UV Commands for this Project

```bash
# Install dependencies
uv sync

# Install with dev dependencies  
uv sync --extra dev

# Run the application
uv run python main.py

# Run any Python command in the project environment
uv run python -c "import openai; print('OpenAI available')"

# Add a new dependency
uv add requests

# Add a dev dependency
uv add --dev pytest
```

## File Structure

```
GmailAI/
├── main.py                 # Main application entry point
├── config.py              # Configuration management
├── email_processor.py     # Main email processing logic
├── pyproject.toml         # UV project configuration
├── uv.lock                # UV dependency lockfile
├── uv.toml                # UV settings
├── requirements.txt       # Python dependencies (legacy)
├── .env.example          # Environment variables template
├── README.md             # This file
├── UV_SETUP.md           # UV setup documentation
└── services/
    ├── __init__.py
    ├── email_service.py   # Gmail IMAP service
    ├── ai_service.py      # AI processing service
    ├── whatsapp_service.py # WhatsApp messaging service
    └── calendar_service.py # Google Calendar service
```

## Usage

1. **Automatic Mode**: The application runs daily at 5 PM
2. **Manual Mode**: Uncomment `processor.process_emails()` in `main.py` to run immediately
3. **Testing**: Run individual services for testing

## Customization

- **Email Domain**: Change `EMAIL_DOMAIN` in `config.py`
- **Schedule**: Modify the schedule in `main.py`
- **AI Model**: Switch between GPT-4 and Claude in `config.py`
- **Processing Logic**: Customize email analysis in `ai_service.py`

## Troubleshooting

1. **Gmail Authentication**: Ensure 2FA is enabled and use App Password
2. **AI API Limits**: Check your API usage and limits
3. **WhatsApp**: Verify phone number format and API credentials
4. **Calendar**: Ensure credentials.json is in the correct location

## Security Notes

- Never commit `.env` file to version control
- Keep API keys secure
- Use environment variables for sensitive data
- Regularly rotate API keys
