# 📧 Gmail AI Email Processor

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue)](https://python.org)
[![UV](https://img.shields.io/badge/UV-Package%20Manager-green)](https://github.com/astral-sh/uv)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT%20Integration-orange)](https://openai.com)
[![LangChain](https://img.shields.io/badge/LangChain-Agents-purple)](https://langchain.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An intelligent email processing system that automatically fetches emails from Gmail, analyzes them using AI agents, sends WhatsApp notifications, and creates Google Calendar events. Now features a **modular agent-based architecture** for enhanced flexibility and scalability.

## 🚀 Features

- **🤖 AI Agent Architecture**: Specialized agents for different tasks (Email, Analysis, Notification, Calendar)
- **📨 Gmail Integration**: Secure IMAP access with OAuth2 authentication
- **� AI-Powered Analysis**: Uses OpenAI GPT models to extract events, dates, and summaries
- **📱 WhatsApp Notifications**: Smart notifications via CallMeBot API
- **📅 Calendar Management**: Automatic Google Calendar event creation with duplicate prevention
- **🏗️ Modular Design**: Clean agent-based architecture with specialized functions
- **⚡ Modern Dependencies**: UV package manager for fast, reliable dependency management
- **📊 Comprehensive Logging**: Detailed logging and error handling
- **🎯 Smart Filtering**: Process emails from specific domains only
- **🔧 Multiple Interfaces**: Both agent-based and legacy processing modes

## 🏗️ Agent Architecture

The system uses a coordinator agent that orchestrates four specialized agents:

```mermaid
graph TB
    A[Gmail IMAP] --> B[📧 EmailAgent]
    B --> C[🧠 AnalysisAgent]
    C --> D[📱 NotificationAgent]
    C --> E[📅 CalendarAgent]
    
    F[🎛️ CoordinatorAgent] --> B
    F --> C
    F --> D
    F --> E
    
    C --> G[OpenAI GPT]
    D --> H[CallMeBot API]
    E --> I[Google Calendar API]
    
    style F fill:#ff9
    style B fill:#9ff
    style C fill:#f9f
    style D fill:#9f9
    style E fill:#99f
```

### Agent Responsibilities

- **📧 EmailAgent**: Fetches and manages email data from Gmail
- **🧠 AnalysisAgent**: AI-powered email analysis for summaries and event extraction
- **📱 NotificationAgent**: Handles WhatsApp notifications and message formatting
- **📅 CalendarAgent**: Creates and manages Google Calendar events
- **🎛️ CoordinatorAgent**: Orchestrates the entire workflow between agents

## 📋 Prerequisites

- Python 3.11+
- Gmail account with 2FA and app password
- Google Cloud Console project with Calendar API enabled
- OpenAI API key
- CallMeBot WhatsApp setup

## ⚡ Quick Start

### 1. Install UV Package Manager

```bash
# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Clone and Setup

```bash
git clone https://github.com/YOUR_USERNAME/gmail-ai-processor.git
cd gmail-ai-processor

# Install dependencies
uv sync

# Install with dev dependencies (optional)
uv sync --extra dev
```

### 3. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your credentials
# Also download credentials.json from Google Cloud Console
```

### 4. Run the Processor

#### Agent-Based Mode (Recommended)

```bash
# Run with agent architecture
uv run python main_agent.py --mode agent --max-emails 10

# Get agent system information
uv run python main_agent.py --mode info

# Run health check on all services
uv run python main_agent.py --mode health

# Run on schedule (daily at 5 PM)
uv run python main_agent.py --mode agent --schedule
```

#### Legacy Mode

```bash
# Run legacy processor
uv run python main_agent.py --mode legacy

# Or use the original main.py
uv run python main.py
```

#### Command Options

| Option | Description |
|--------|-------------|
| `--mode agent` | Use the new agent-based architecture |
| `--mode legacy` | Use the original processor |
| `--mode info` | Show agent system information |
| `--mode health` | Run health check on all services |
| `--max-emails N` | Process maximum N emails (default: 10) |
| `--schedule` | Run on schedule instead of once |
| `--create-env` | Create example .env file |

## 🔧 Configuration

### Environment Variables (`.env`)

```bash
# Gmail IMAP Configuration
GMAIL_USER=your_email@gmail.com
GMAIL_APP_PASSWORD=your_16_char_app_password

# OpenAI Configuration
OPENAI_API_KEY=sk-your_openai_api_key

# WhatsApp Configuration (CallMeBot)
CALLMEBOT_API_KEY=your_callmebot_api_key
CALLMEBOT_PHONE=65123456789

# Domain Filter (optional)
EMAIL_DOMAIN=@company.com  # Filter emails from specific domain. Leave empty for all emails

# Google Calendar (place credentials.json in project root)
GOOGLE_CALENDAR_CREDENTIALS_FILE=credentials.json
GOOGLE_CALENDAR_TOKEN_FILE=token.json
```

### Required Files

1. **`.env`** - Copy from `.env.example` and fill in your credentials
2. **`credentials.json`** - Download from Google Cloud Console (Calendar API)

## 📁 Project Structure

```
gmail-ai-processor/
├── 📄 main_agent.py           # New agent-based entry point
├── 📄 main.py                 # Legacy entry point
├── 📄 email_processor.py      # Legacy orchestrator
├── 📄 agent_email_processor.py # Agent-based orchestrator
├── 📄 config.py              # Configuration management
├── 📁 agents/                # Agent-based architecture
│   ├── 📄 __init__.py
│   ├── 📄 base_agent.py       # Base agent class
│   ├── 📄 coordinator_agent.py # Main workflow coordinator
│   ├── 📄 email_agent.py      # Email fetching and processing
│   ├── 📄 analysis_agent.py   # AI-powered email analysis
│   ├── 📄 notification_agent.py # WhatsApp notifications
│   └── 📄 calendar_agent.py   # Calendar event management
├── 📁 services/              # Modular services (legacy)
│   ├── 📄 email_service.py    # Gmail IMAP integration
│   ├── 📄 ai_service.py       # OpenAI GPT integration
│   ├── 📄 whatsapp_service.py # WhatsApp notifications
│   └── 📄 calendar_service.py # Google Calendar with duplicates prevention
├── 📄 pyproject.toml         # UV configuration with LangChain
├── 📄 uv.lock               # Dependency lock file
├── 📄 .env.example          # Environment template
├── 📄 .gitignore            # Git ignore rules
└── 📁 docs/                 # Documentation and diagrams
    ├── 📄 architecture_diagram.puml
    ├── 📄 sequence_diagram.puml
    └── 📄 UV_SETUP.md
```

## 🎯 Key Features Explained

### 🤖 Agent-Based Architecture
- **Modular Design**: Each agent handles a specific responsibility
- **Coordinated Workflow**: Coordinator agent orchestrates the entire process
- **Specialized Functions**: Each agent provides specific functions and tools
- **Health Monitoring**: Built-in health checks for all services
- **Flexible Execution**: Can run individual agent functions or full workflow

### 🧠 AI Email Analysis
- Extracts event details (title, date, time, location)
- Generates concise email summaries
- Determines if calendar events should be created
- Handles multiple events in a single email
- Priority and sentiment analysis
- Action item extraction

### 📅 Smart Calendar Integration
- **Duplicate Prevention**: Checks existing events before creating new ones
- **Smart Defaults**: Uses 7 AM - 8 AM for events with missing times
- **Timezone Support**: Handles Singapore timezone by default
- **Batch Processing**: Creates multiple events from single emails

### 📱 WhatsApp Notifications
- Real-time notifications for processed emails
- Formatted messages with email summaries
- Calendar event creation status
- Powered by CallMeBot API

## 🛠️ Development

### Using Traditional Python (Alternative)

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run
python main.py
```

### VS Code Tasks

The project includes VS Code tasks for common operations:
- `Run Email Processor (UV)`
- `Install Dependencies (UV)`
- `Install Dev Dependencies (UV)`

### Testing

```bash
# Test project structure
uv run python test_structure.py

# Manual testing
uv run python main.py
```

## 📊 Monitoring & Logging

- **Log File**: `email_processor.log`
- **Log Levels**: INFO, WARNING, ERROR
- **Features Logged**:
  - Email processing status
  - AI analysis results
  - WhatsApp delivery status
  - Calendar event creation/skipping
  - Error tracking and debugging

## 🐛 Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| Gmail Authentication Failed | Enable 2FA and generate app password |
| Google Calendar API Error | Enable Calendar API in Google Cloud Console |
| OpenAI API Error | Check API key and billing status |
| WhatsApp Not Sending | Verify CallMeBot setup and phone number format |
| Duplicate Events | Check calendar service logs for duplicate detection |

### Debug Steps

1. Check `email_processor.log` for detailed error messages
2. Verify all credentials in `.env` file
3. Test individual services separately
4. Ensure all required APIs are enabled

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [UV Package Manager](https://github.com/astral-sh/uv) for modern Python dependency management
- [OpenAI](https://openai.com) for powerful AI capabilities
- [CallMeBot](https://www.callmebot.com) for WhatsApp API
- [Google Calendar API](https://developers.google.com/calendar) for calendar integration

## 📞 Support

- 📋 **Issues**: [GitHub Issues](https://github.com/YOUR_USERNAME/gmail-ai-processor/issues)
- 📖 **Documentation**: Check the `docs/` folder
- 🔍 **Debugging**: Review `email_processor.log`

---

⭐ **Star this repository if you find it helpful!**
