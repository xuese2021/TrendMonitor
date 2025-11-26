import os
import sys
import logging
from history import HistoryManager
from summarizer import DailySummarizer
from notifier import TelegramNotifier

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Generate and send daily summary"""
    # Get secrets from environment variables
    token = os.environ.get('TELEGRAM_BOT_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')

    if not token or not chat_id:
        logger.error("TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID must be set")
        sys.exit(1)

    logger.info("Starting Daily Summary generation...")
    
    try:
        # Initialize components
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        history_file = os.path.join(project_root, 'data', 'history.json')
        history_manager = HistoryManager(history_file)
        
        # Clean old entries (older than 7 days)
        history_manager.clean_old(days=7)
        
        # Generate summary
        summarizer = DailySummarizer(history_manager)
        summary = summarizer.generate_summary(hours=24, top_n=30)
        
        if not summary:
            logger.info("No trends to summarize")
            return
        
        logger.info(f"Generated summary with {len(summary)} top trends")
        
        # Format and send message
        message = summarizer.format_daily_message(summary, hours=24)
        
        notifier = TelegramNotifier(token, chat_id)
        if notifier.send_message(message):
            logger.info("Daily summary sent successfully")
        else:
            logger.error("Failed to send daily summary")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"An error occurred: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
