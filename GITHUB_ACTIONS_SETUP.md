# GitHub Actions Setup Guide

## 🚀 Automated Daily Email Processing with GitHub Actions

Your Gmail AI Processor will now run automatically at **6 PM Singapore Time** every day using GitHub Actions (cloud-based, no server needed).

## 📋 Setup Steps

### 1. Add Repository Secrets

Go to your GitHub repository: `https://github.com/sabven/gmail-ai-processor`

Navigate to: **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

Add these secrets one by one:

#### Gmail Configuration
- `GMAIL_USER` → `your_gmail_address@gmail.com`
- `GMAIL_APP_PASSWORD` → `your_gmail_app_password`

#### OpenAI Configuration  
- `OPENAI_API_KEY` → `your_openai_api_key_here`

#### WhatsApp Configuration (Primary)
- `CALLMEBOT_API_KEY` → `your_primary_callmebot_api_key`
- `CALLMEBOT_PHONE` → `your_primary_phone_number`

#### WhatsApp Configuration (Secondary)
- `CALLMEBOT_API_KEY_2` → `your_secondary_callmebot_api_key`
- `CALLMEBOT_PHONE_2` → `your_secondary_phone_number`

#### Google Calendar Configuration
- `CREDENTIALS_JSON` → Copy the entire contents of your `credentials.json` file

### 2. Enable GitHub Actions

1. Go to your repository's **Actions** tab
2. Enable workflows if prompted
3. The workflow will appear as "Gmail AI Processor - Daily Run"

### 3. Test the Setup

#### Manual Test
1. Go to **Actions** tab
2. Click on "Gmail AI Processor - Daily Run"
3. Click **Run workflow** → **Run workflow**
4. Monitor the execution logs

#### Scheduled Run
- Automatically runs at **6:00 PM Singapore Time** (10:00 AM UTC) daily
- Check the **Actions** tab for execution history and logs

## 🔧 Features

✅ **Runs in the Cloud** - No need for your computer to be on
✅ **Secure** - All credentials stored as GitHub Secrets
✅ **Free** - Uses GitHub's free tier (2,000 minutes/month)
✅ **Reliable** - Automatic execution with error logging
✅ **Manual Override** - Can trigger manually anytime

## 📊 Monitoring

- **Execution Logs**: Available in Actions tab for 90 days
- **Email Notifications**: GitHub can email you if workflow fails
- **WhatsApp Messages**: You'll receive summaries if CallMeBot is working
- **Email Fallback**: Notification emails if WhatsApp fails

## ⚙️ Customization

### Change Schedule
Edit `.github/workflows/daily-email-processor.yml`:
```yaml
schedule:
  - cron: '0 10 * * *'  # 6 PM SGT (UTC+8)
```

### Different Time Examples:
- `'0 2 * * *'` = 10 AM SGT (2 AM UTC)
- `'0 14 * * *'` = 10 PM SGT (2 PM UTC)
- `'0 10 * * 1-5'` = 6 PM SGT, Monday-Friday only

## 🚨 Important Notes

1. **Credentials Security**: Never commit credentials to the repository
2. **Rate Limits**: GitHub Actions has usage limits on free tier
3. **Calendar Auth**: First run might need manual token refresh
4. **Time Zone**: Schedule uses UTC, converted to Singapore Time

## 🆘 Troubleshooting

- **Check Actions tab** for execution logs
- **Manual trigger** to test configuration
- **Secrets validation** - ensure all secrets are correctly set
- **Dependencies** - workflow installs requirements automatically

Your Gmail AI Processor is now fully automated! 🎉
