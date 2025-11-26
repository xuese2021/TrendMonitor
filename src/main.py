import os
import sys
import logging
import time
from datetime import datetime
from fetcher import TrendFetcher
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
    从 config/frequency_words.txt 加载关键词
    支持语法：
    - 普通关键词：直接匹配
    - 必须词 +词汇：必须同时包含
    - 过滤词 !词汇：排除包含此词的结果
    """
    # 获取项目根目录（src 的父目录）
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_file = os.path.join(project_root, 'config', 'frequency_words.txt')
    
    if not os.path.exists(config_file):
        logger.warning(f"配置文件不存在: {config_file}")
        logger.info("未配置关键词，将显示所有热点")
        return []
    
    keyword_groups = []
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # 跳过空行和注释
                if not line or line.startswith('#'):
                    continue
                
                # 解析关键词组
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
        
        logger.info(f"已加载 {len(keyword_groups)} 个关键词组")
        return keyword_groups
    
    except Exception as e:
        logger.error(f"加载关键词配置失败: {e}")
        return []

def filter_by_keywords(trends, keyword_groups):
    """
    根据关键词组过滤热点
    """
    if not keyword_groups:
        return trends
    
    filtered_trends = {}
    
    for platform, items in trends.items():
        filtered_items = []
        
        for item in items:
            title = item['title'].lower()
            
            # 检查每个关键词组
            for group in keyword_groups:
                # 检查是否包含排除词
                if any(excluded.lower() in title for excluded in group['excluded']):
                    continue
                
                # 检查是否包含必须词
                if group['required']:
                    if not all(required.lower() in title for required in group['required']):
                        continue
                
                # 检查是否包含普通关键词（任意一个即可）
                if group['normal']:
                    if any(keyword.lower() in title for keyword in group['normal']):
                        filtered_items.append(item)
                        break
                elif group['required']:
                    # 如果只有必须词，没有普通关键词
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

    logger.info("Starting TrendMonitor...")
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
        
        # 记录抓取结果到 metrics
        for platform, items in trends.items():
            metrics_tracker.record_platform_attempt(platform)
            if items:
                metrics_tracker.record_platform_success(platform, len(items))
            else:
                metrics_tracker.record_platform_failure(platform, 'No data')
        
        # 加载并应用关键词过滤
        keyword_groups = load_keywords()
        if keyword_groups:
            logger.info(f"应用关键词过滤...")
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
             logger.info("没有新的热点需要推送")

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
                # Check if batch is full (10 items)
                if len(batch) < batch_size:
                    logger.info(f"Batch {i+1} has only {len(batch)} items. Ignoring (threshold is {batch_size}).")
                    continue
                
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
        success_rate = metrics_tracker.current_run.get('success_rate', 0)
        if config.should_send_alerts() and success_rate < config.get_min_success_rate():
            if token and chat_id:
                alert_msg = f"⚠️ 警告：抓取成功率过低\n\n{metrics_tracker.get_summary()}"
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
