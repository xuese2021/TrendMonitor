import os
import sys
import logging
import time
from datetime import datetime, timezone, timedelta
from fetcher import TrendFetcher

# Set UTC+8 timezone
UTC_PLUS_8 = timezone(timedelta(hours=8))
from notifier import TelegramNotifier
from history import HistoryManager
from config_loader import ScrapingConfig
from cache_manager import CacheManager
from metrics_tracker import MetricsTracker
from fetcher_wrapper import get_fetcher_wrapper

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_keywords():
    """
    Load keywords from config/frequency_words.txt
    Supported syntax:
    - Regular keywords: direct match
    - Required words (+word): must contain all
    - Excluded words (!word): exclude results containing this word
    """
    # Get project root directory (parent of src)
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_file = os.path.join(project_root, 'config', 'frequency_words.txt')
    
    if not os.path.exists(config_file):
        logger.warning(f"Config file not found: {config_file}")
        logger.info("No keywords configured, showing all trends")
        return []
    
    keyword_groups = []
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                
                # Parse keyword groups
                words = line.split()
                normal_keywords = []
                required_keywords = []
                excluded_keywords = []
                
                for word in words:
                    if word.startswith('+'):
                        required_keywords.append(word[1:])
                    elif word.startswith('!'):
                        excluded_keywords.append(word[1:])
                    else:
                        normal_keywords.append(word)
                
                if normal_keywords or required_keywords:
                    keyword_groups.append({
                        'normal': normal_keywords,
                        'required': required_keywords,
                        'excluded': excluded_keywords
                    })
        
        logger.info(f"Loaded {len(keyword_groups)} keyword groups")
        return keyword_groups
    
    except Exception as e:
        logger.error(f"Failed to load keyword config: {e}")
        return []

def filter_by_keywords(trends, keyword_groups):
    """
    Filter trends by keyword groups
    """
    if not keyword_groups:
        return trends
    
    filtered_trends = {}
    
    for platform, items in trends.items():
        filtered_items = []
        
        for item in items:
            title = item['title'].lower()
            
            # Check each keyword group
            for group in keyword_groups:
                # Check for excluded words
                if any(excluded.lower() in title for excluded in group['excluded']):
                    continue
                
                # Check for required words
                if group['required']:
                    if not all(required.lower() in title for required in group['required']):
                        continue
                
                # Check for normal keywords (any match is enough)
                if group['normal']:
                    if any(keyword.lower() in title for keyword in group['normal']):
                        filtered_items.append(item)
                        break
                elif group['required']:
                    # If only required words, no normal keywords
                    filtered_items.append(item)
                    break
        
        if filtered_items:
            filtered_trends[platform] = filtered_items
    
    return filtered_trends

def filter_new_items(trends, history_manager):
    """
    Filter out items that have already been sent
    """
    new_trends = {}
    for platform, items in trends.items():
        new_items = []
        for item in items:
            if not history_manager.is_sent(item['url']):
                new_items.append(item)
        
        if new_items:
            new_trends[platform] = new_items
            
    return new_trends

def main():
    # Get secrets from environment variables
    token = os.environ.get('TELEGRAM_BOT_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    force_push = os.environ.get('FORCE_PUSH') == '1'

    if not token or not chat_id:
        logger.warning("TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID not set. Running in dry-run mode (console output only).")

    # Get UTC+8 time
    now_utc8 = datetime.now(UTC_PLUS_8)
    logger.info(f"Starting TrendMonitor... (Beijing Time: {now_utc8.strftime('%Y-%m-%d %H:%M:%S')})")
    start_time = datetime.now()
    
    try:
        # Initialize systems
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        history_file = os.path.join(project_root, 'data', 'history.json')
        cache_file = os.path.join(project_root, 'data', 'cache.json')
        metrics_file = os.path.join(project_root, 'data', 'metrics.json')
        
        config = ScrapingConfig()
        history_manager = HistoryManager(history_file)
        cache_manager = CacheManager(cache_file)
        metrics_tracker = MetricsTracker(metrics_file)
        
        logger.info("Initialized monitoring and caching systems")
        
        # Cleanup old cache
        cache_manager.cleanup_old()
        
        fetcher = TrendFetcher()
        wrapper = get_fetcher_wrapper(fetcher, config, cache_manager, metrics_tracker)
        
        # Fetch all with monitoring
        trends = fetcher.fetch_all()
        
        # Record fetch results to metrics
        for platform, items in trends.items():
            metrics_tracker.record_platform_attempt(platform)
            if items:
                metrics_tracker.record_platform_success(platform, len(items))
            else:
                metrics_tracker.record_platform_failure(platform, 'No data')
        
        # Load and apply keyword filtering
        keyword_groups = load_keywords()
        if keyword_groups:
            logger.info("Applying keyword filtering...")
            trends = filter_by_keywords(trends, keyword_groups)
        
        if not force_push:
            logger.info("Filtering out already sent items...")
            trends = filter_new_items(trends, history_manager)
        else:
            logger.info("Force push enabled, skipping de-duplication")

        # Log stats
        total_items = 0
        for platform, items in trends.items():
            count = len(items)
            total_items += count
            logger.info(f"Fetched {count} new items from {platform}")
        
        # Save metrics
        metrics_tracker.save_metrics()
        elapsed_time = (datetime.now() - start_time).total_seconds()
        logger.info(f"Execution time: {elapsed_time:.2f}s")
        
        # Log summary
        logger.info(metrics_tracker.get_summary())
        
        if total_items == 0:
             logger.info("No new trends to push")

        if token and chat_id and trends:
            # Flatten trends into a list of (platform, item) tuples
            all_items = []
            for platform, items in trends.items():
                for item in items:
                    all_items.append((platform, item))
            
            # Batch items in groups of 10
            batch_size = 10
            batches = [all_items[i:i + batch_size] for i in range(0, len(all_items), batch_size)]
            
            logger.info(f"Total items: {len(all_items)}. Created {len(batches)} batches.")
            
            for i, batch in enumerate(batches):
                # Send all batches, no longer skip small batches
                logger.info(f"Processing batch {i+1}/{len(batches)} with {len(batch)} items...")
                
                # Reconstruct trends dict for this batch
                batch_trends = {}
                for platform, item in batch:
                    if platform not in batch_trends:
                        batch_trends[platform] = []
                    batch_trends[platform].append(item)
                
                # Send notification
                logger.info("Sending notification to Telegram...")
                try:
                    notifier = TelegramNotifier(token, chat_id)
                    message = notifier.format_trends(batch_trends)
                    
                    if not message:
                        logger.warning(f"Batch {i+1} resulted in empty message, skipping.")
                        continue

                    if notifier.send_message(message):
                        logger.info(f"Batch {i+1} sent successfully.")
                        # Update history only for sent items
                        for platform, items in batch_trends.items():
                            for item in items:
                                history_manager.add(item)
                        history_manager.save_history()
                    else:
                        logger.error(f"Failed to send batch {i+1}.")
                        # Don't exit immediately, try next batch but mark run as failed
                        # sys.exit(1) 
                except Exception as e:
                    logger.error(f"Error processing batch {i+1}: {e}", exc_info=True)
        
        # Check success rate and send alert if needed
        total_platforms = metrics_tracker.current_run.get('total_platforms', 0)
        success_count = metrics_tracker.current_run.get('success_count', 0)
        success_rate = (success_count / total_platforms) if total_platforms > 0 else 0
        
        if config.should_send_alerts() and success_rate < config.get_min_success_rate():
            if token and chat_id:
                alert_msg = f"Warning: Low fetch success rate\n\n{metrics_tracker.get_summary()}"
                notifier = TelegramNotifier(token, chat_id)
                notifier.send_message(alert_msg)
                logger.warning(f"Low success rate alert sent: {success_rate:.1%}")
        
        elif trends:
            # Dry-run mode with content
            logger.info("Printing trends to console:")
            for platform, items in trends.items():
                print(f"\n=== {platform} ===")
                for item in items:
                    print(f"- {item['title']} ({item['url']})")

    except Exception as e:
        logger.error(f"An error occurred: {e}", exc_info=True)
        # Cleanup browser if it was initialized
        try:
            from fetcher_browser import cleanup_browser
            cleanup_browser()
        except Exception:
            pass
        sys.exit(1)
    finally:
        # Always cleanup browser on exit
        try:
            from fetcher_browser import cleanup_browser
            cleanup_browser()
        except Exception:
            pass

if __name__ == "__main__":
    main()
