# Gmail AI Email Processor - Flow Diagram

## 🔄 **Main Application Flow**

```
┌─────────────────────────────────────────────────────────────────────┐
│                           MAIN.PY                                  │
│                    (Application Entry Point)                       │
└─────────────────────┬───────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        CONFIG.PY                                   │
│    • Load .env variables                                           │
│    • Initialize Gmail, AI, WhatsApp, Calendar settings             │
│    • Validate required credentials                                 │
└─────────────────────┬───────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   EMAIL_PROCESSOR.PY                               │
│                 (Main Processing Logic)                            │
└─────────────────────┬───────────────────────────────────────────────┘
                      │
                      ▼
              ┌───────────────┐
              │   SCHEDULER   │
              │   (5 PM Daily)│
              └───────┬───────┘
                      │
                      ▼
```

## 📧 **Email Processing Flow**

```
┌─────────────────────────────────────────────────────────────────────┐
│                    EMAIL_SERVICE.PY                                │
│                  (Gmail IMAP Service)                              │
└─────────────────────┬───────────────────────────────────────────────┘
                      │
                      ▼
        ┌─────────────────────────────────┐
        │    Connect to Gmail IMAP        │
        │    • Server: imap.gmail.com     │
        │    • Port: 993 (SSL)            │
        │    • Auth: App Password         │
        └─────────────┬───────────────────┘
                      │
                      ▼
        ┌─────────────────────────────────┐
        │    Search for Emails            │
        │    • Domain: @dcis.com          │
        │    • Date: Last 1 day           │
        │    • Limit: Last 10 emails      │
        └─────────────┬───────────────────┘
                      │
                      ▼
        ┌─────────────────────────────────┐
        │    Extract Email Data           │
        │    • Subject                    │
        │    • From                       │
        │    • Date                       │
        │    • Body (Plain Text)          │
        └─────────────┬───────────────────┘
                      │
                      ▼
                   [Email Data]
```

## 🤖 **AI Processing Flow**

```
                   [Email Data]
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     AI_SERVICE.PY                                  │
│                  (AI Analysis Service)                             │
└─────────────────────┬───────────────────────────────────────────────┘
                      │
                      ▼
        ┌─────────────────────────────────┐
        │    Choose AI Provider           │
        │    • OpenAI GPT-4               │
        │    • Anthropic Claude           │
        └─────────────┬───────────────────┘
                      │
                      ▼
        ┌─────────────────────────────────┐
        │    Send Analysis Prompt         │
        │    • Summarize email (gist)     │
        │    • Detect events/meetings     │
        │    • Extract event details      │
        └─────────────┬───────────────────┘
                      │
                      ▼
        ┌─────────────────────────────────┐
        │    Parse AI Response            │
        │    • JSON format                │
        │    • Gist summary               │
        │    • Event detection flag       │
        │    • Event details              │
        └─────────────┬───────────────────┘
                      │
                      ▼
                 [AI Analysis Result]
```

## 📱 **WhatsApp Notification Flow**

```
              [AI Analysis Result]
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────────┐
│                  WHATSAPP_SERVICE.PY                               │
│                (WhatsApp Messaging Service)                        │
└─────────────────────┬───────────────────────────────────────────────┘
                      │
                      ▼
        ┌─────────────────────────────────┐
        │    Choose WhatsApp Provider     │
        │    • Twilio WhatsApp API        │
        │    • CallMeBot API              │
        └─────────────┬───────────────────┘
                      │
                      ▼
        ┌─────────────────────────────────┐
        │    Format Message               │
        │    📧 Email Summary:            │
        │    From: [sender]               │
        │    Subject: [subject]           │
        │    📝 Gist: [ai_summary]        │
        │    📅 [calendar_event_notice]   │
        └─────────────┬───────────────────┘
                      │
                      ▼
        ┌─────────────────────────────────┐
        │    Send WhatsApp Message        │
        │    • API Call                   │
        │    • Error Handling             │
        │    • Success Logging            │
        └─────────────────────────────────┘
```

## 📅 **Calendar Integration Flow**

```
              [AI Analysis Result]
                      │
                      ▼
                ┌─────────────┐
                │  Has Event? │
                └─────┬───────┘
                      │
               ┌──────▼──────┐
               │ YES    NO   │
               │             │
               ▼             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                 CALENDAR_SERVICE.PY                                │
│               (Google Calendar Service)                            │
└─────────────────────┬───────────────────────────────────────────────┘
                      │
                      ▼
        ┌─────────────────────────────────┐
        │    Setup Google Calendar        │
        │    • Load credentials.json      │
        │    • OAuth2 Authentication      │
        │    • Save token.json            │
        └─────────────┬───────────────────┘
                      │
                      ▼
        ┌─────────────────────────────────┐
        │    Create Calendar Event        │
        │    • Title: [from AI]           │
        │    • Description: [details]     │
        │    • Start/End Time             │
        │    • Location                   │
        │    • Email Reminders            │
        └─────────────┬───────────────────┘
                      │
                      ▼
        ┌─────────────────────────────────┐
        │    Insert Event to Calendar     │
        │    • Google Calendar API        │
        │    • Primary Calendar           │
        │    • Return Event Link          │
        └─────────────────────────────────┘
```

## 🔧 **Complete System Architecture**

```
┌─────────────────────────────────────────────────────────────────────┐
│                           MAIN.PY                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐│
│  │   CONFIG    │  │  SCHEDULER  │  │   LOGGER    │  │    ENV      ││
│  │   .env      │  │ 5 PM Daily  │  │   .log      │  │ Validation  ││
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘│
└─────────────────────────┬───────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   EMAIL_PROCESSOR.PY                               │
│                    (Orchestrator)                                  │
└─────────────────────┬───────────────────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        │             │             │
        ▼             ▼             ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│EMAIL_SERVICE│ │ AI_SERVICE  │ │WHATSAPP_SRV │ │CALENDAR_SRV │
│             │ │             │ │             │ │             │
│Gmail IMAP   │ │OpenAI/Claude│ │Twilio/      │ │Google       │
│• Fetch      │ │• Analyze    │ │CallMeBot    │ │Calendar     │
│• Parse      │ │• Summarize  │ │• Notify     │ │• Create     │
│• Extract    │ │• Detect     │ │• Format     │ │• Schedule   │
└─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘
```

## 📊 **Data Flow Sequence**

```
1. [SCHEDULER] ──── Triggers at 5 PM ────► [EMAIL_PROCESSOR]
                                               │
2. [EMAIL_PROCESSOR] ──── Fetch Emails ────► [EMAIL_SERVICE]
                                               │
3. [EMAIL_SERVICE] ──── Email Data ────────► [AI_SERVICE]
                                               │
4. [AI_SERVICE] ──── Analysis Result ──────► [EMAIL_PROCESSOR]
                                               │
5. [EMAIL_PROCESSOR] ──── Parallel Processing ─┬─► [WHATSAPP_SERVICE]
                                                 │
                                                 └─► [CALENDAR_SERVICE]
                                                     (if event detected)
```

## 🔄 **Error Handling & Retry Logic**

```
┌─────────────────────────────────────────────────────────────────────┐
│                      ERROR HANDLING                                │
├─────────────────────────────────────────────────────────────────────┤
│  Gmail Connection Error     │  Retry with exponential backoff      │
│  AI API Rate Limit         │  Wait and retry, fallback provider   │
│  WhatsApp Send Failure     │  Try alternative provider            │
│  Calendar Auth Error       │  Skip calendar, continue processing  │
│  Network Timeout           │  Retry with timeout increase         │
└─────────────────────────────────────────────────────────────────────┘
```

## 🔐 **Security & Configuration**

```
┌─────────────────────────────────────────────────────────────────────┐
│                        SECURITY FLOW                               │
├─────────────────────────────────────────────────────────────────────┤
│  .env File Loading          │  Environment variables               │
│  Gmail App Password         │  2FA + App-specific password         │
│  API Keys Validation        │  Check existence and format          │
│  OAuth2 Tokens             │  Google Calendar authentication       │
│  Secure Storage            │  No credentials in code              │
└─────────────────────────────────────────────────────────────────────┘
```

This flow diagram shows the complete architecture and data flow of your Gmail AI Email Processor system!
