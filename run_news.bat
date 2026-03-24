@echo off
REM Daily AI News Generator - Run Script
REM Set your Anthropic API key below before first run

SET ANTHROPIC_API_KEY=REPLACE_WITH_YOUR_ANTHROPIC_API_KEY
SET GITHUB_TOKEN=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
SET REPO_PATH=C:\Users\cdhed\.code\.ai-news

echo [%date% %time%] Starting AI News generation...
"C:\Users\cdhed\AppData\Local\Programs\Python\Python39\python.exe" "%REPO_PATH%\generate_news.py"

IF %ERRORLEVEL% NEQ 0 (
    echo [%date% %time%] ERROR: Script failed with code %ERRORLEVEL%
    exit /b %ERRORLEVEL%
)

echo [%date% %time%] Done.
