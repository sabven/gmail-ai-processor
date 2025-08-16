@echo off
REM Gmail AI Processor - Daily Runner
REM This batch file runs the email processor

echo Starting Gmail AI Processor at %date% %time%

REM Change to the project directory
cd /d "C:\Sabaresh\GmailAI"

REM Activate the environment and run the processor
python main.py

echo Gmail AI Processor completed at %date% %time%

REM Optional: Keep window open for debugging (remove in production)
REM pause
