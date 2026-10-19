# Free Fire Info Telegram Bot

## Setup

1. Install Python 3.10 or newer.
2. Install dependencies: `pip install -r requirements.txt`.
3. Set the environment variable `TELEGRAM_BOT_TOKEN` to your Telegram bot token.
4. Run: `python info.py`.

### GitHub Actions / Secrets

Add a repository secret named `TELEGRAM_BOT_TOKEN` in **Settings → Secrets and variables → Actions**. The secret is not used automatically; a workflow must explicitly pass it to the process. Never commit bot tokens into source code.

## Notes

This repository contains the bot source and dependencies. The source file was syntax-checked locally, but API endpoints and live bot behavior have not been tested.
