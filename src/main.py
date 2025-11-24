import os
import sys
import logging
from fetcher import TrendFetcher
from notifier import TelegramNotifier

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Keywords to filter trends.
# If empty, all trends are reported.
# If populated, only trends containing at least one keyword (case-insensitive) are reported.
KEYWORDS = [] 

def main():
    # Get secrets from environment variables
    token = os.environ.get('TELEGRAM_BOT_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')

    if not token or not chat_id:
        logger.warning("TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID not set. Running in dry-run mode (console output only).")

    logger.info("Starting TrendMonitor...")
    
    try:
        fetcher = TrendFetcher()
        trends = fetcher.fetch_all()
        
        # Filter trends if keywords are set
        if KEYWORDS:
            logger.info(f"Filtering trends with keywords: {KEYWORDS}")
            filtered_trends = {}
            for platform, items in trends.items():
                filtered_items = []
                for item in items:
                    # Check if any keyword is in the title (case-insensitive)
                    if any(keyword.lower() in item['title'].lower() for keyword in KEYWORDS):
                        filtered_items.append(item)
                
                if filtered_items:
                    filtered_trends[platform] = filtered_items
            trends = filtered_trends
        
        # Log stats
        total_items = 0
        for platform, items in trends.items():
            count = len(items)
            total_items += count
            logger.info(f"Fetched {count} items from {platform}")

        if total_items == 0 and KEYWORDS:
             logger.info("No trends matched the keywords.")

        if token and chat_id and trends:
            logger.info("Sending notification to Telegram...")
            notifier = TelegramNotifier(token, chat_id)
            message = notifier.format_trends(trends)
            if notifier.send_message(message):
                logger.info("Notification sent successfully.")
            else:
                logger.error("Failed to send notification.")
        else:
            logger.info("Printing trends to console:")
            for platform, items in trends.items():
                print(f"\n=== {platform} ===")
                for item in items:
                    print(f"- {item['title']} ({item['url']})")

    except Exception as e:
        logger.error(f"An error occurred: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
