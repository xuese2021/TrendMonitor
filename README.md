# TrendMonitor

A real-time trend monitoring application inspired by [TopList](https://github.com/tophubs/TopList) and [TrendRadar](https://github.com/xuese2021/TrendRadar).

## Features
- Monitors real-time trends from **Weibo**, **Zhihu**, and **Baidu**.
- Sends updates to a **Telegram** channel.
- Automated execution via **GitHub Actions**.

## Setup

### Local Execution
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Set environment variables (optional, for Telegram support):
   ```bash
   export TELEGRAM_BOT_TOKEN="your_bot_token"
   export TELEGRAM_CHAT_ID="your_chat_id"
   ```
3. Run the script:
   ```bash
   python src/main.py
   ```

### GitHub Actions Deployment
1. Fork or push this repository to GitHub.
2. Go to **Settings** > **Secrets and variables** > **Actions**.
3. Add the following repository secrets:
   - `TELEGRAM_BOT_TOKEN`: Your Telegram Bot Token.
   - `TELEGRAM_CHAT_ID`: Your Telegram Chat ID.
4. The workflow will run automatically every day at midnight UTC, or you can trigger it manually from the **Actions** tab.

## Structure
- `src/fetcher.py`: Logic to scrape trending topics.
- `src/notifier.py`: Logic to send Telegram messages.
- `src/main.py`: Entry point.
- `.github/workflows/daily_monitor.yml`: CI/CD configuration.

## License
MIT
