import os
import sys
import logging
from fetcher import TrendFetcher
from notifier import TelegramNotifier

from history import HistoryManager

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

    if not token or not chat_id:
        logger.warning("TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID not set. Running in dry-run mode (console output only).")

    logger.info("Starting TrendMonitor...")
    
    try:
        # Initialize HistoryManager
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        history_file = os.path.join(project_root, 'data', 'history.json')
        history_manager = HistoryManager(history_file)

        fetcher = TrendFetcher()
        trends = fetcher.fetch_all()
        
        # 加载并应用关键词过滤
        keyword_groups = load_keywords()
        if keyword_groups:
            logger.info(f"应用关键词过滤...")
            trends = filter_by_keywords(trends, keyword_groups)
        
        # Filter out already sent items
        logger.info("Filtering out already sent items...")
        trends = filter_new_items(trends, history_manager)

        # Log stats
        total_items = 0
        for platform, items in trends.items():
            count = len(items)
            total_items += count
            logger.info(f"Fetched {count} new items from {platform}")

        if total_items == 0:
             logger.info("没有新的热点需要推送")

        if token and chat_id and trends:
            logger.info("Sending notification to Telegram...")
            notifier = TelegramNotifier(token, chat_id)
            message = notifier.format_trends(trends)
            if notifier.send_message(message):
                logger.info("Notification sent successfully.")
                # Update history
                for platform, items in trends.items():
                    for item in items:
                        history_manager.add(item['url'])
                history_manager.save_history()
            else:
                logger.error("Failed to send notification.")
        else:
            logger.info("Printing trends to console:")
            for platform, items in trends.items():
                print(f"\n=== {platform} ===")
                for item in items:
                    print(f"- {item['title']} ({item['url']})")
                    # In dry-run, we might not want to update history, or maybe we do?
                    # Let's assume dry-run doesn't update history to allow testing.

    except Exception as e:
        logger.error(f"An error occurred: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
