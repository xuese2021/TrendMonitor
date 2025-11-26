from datetime import datetime, timedelta
from collections import Counter
import logging

logger = logging.getLogger(__name__)

class DailySummarizer:
    def __init__(self, history_manager):
        self.history_manager = history_manager

    def aggregate_trends(self, hours=24):
        """Collect trends from the past N hours"""
        recent_trends = self.history_manager.get_recent(hours)
        logger.info(f"Found {len(recent_trends)} trends from the last {hours} hours")
        return recent_trends

    def rank_trends(self, trends, top_n=30):
        """
        Rank trends by frequency and recency
        Returns top N trends with scores
        """
        if not trends:
            return []

        # Count title frequency (similar titles are grouped)
        title_counter = Counter()
        title_data = {}  # Store first occurrence data for each title
        
        for trend in trends:
            title = trend['title']
            # Simple normalization: lowercase and strip
            normalized_title = title.lower().strip()
            
            if normalized_title not in title_data:
                title_data[normalized_title] = trend
            
            title_counter[normalized_title] += 1

        # Calculate scores based on frequency and recency
        scored_trends = []
        now = datetime.now()
        
        for normalized_title, count in title_counter.items():
            trend = title_data[normalized_title]
            
            # Calculate recency score (newer = higher score)
            try:
                timestamp = datetime.fromisoformat(trend['timestamp'])
                hours_old = (now - timestamp).total_seconds() / 3600
                recency_score = max(0, 1 - (hours_old / 24))  # 0-1 score
            except Exception:
                recency_score = 0.5  # Default mid-range score
            
            # Combined score: frequency (70%) + recency (30%)
            score = (count * 0.7) + (recency_score * 0.3)
            
            scored_trends.append({
                'title': trend['title'],  # Original title
                'url': trend['url'],
                'platform': trend['platform'],
                'count': count,
                'score': score,
                'timestamp': trend['timestamp']
            })

        # Sort by score descending
        scored_trends.sort(key=lambda x: x['score'], reverse=True)
        
        return scored_trends[:top_n]

    def generate_summary(self, hours=24, top_n=30):
        """Generate a daily summary of top trends"""
        trends = self.aggregate_trends(hours)
        ranked_trends = self.rank_trends(trends, top_n)
        
        logger.info(f"Generated summary with {len(ranked_trends)} top trends")
        return ranked_trends

    def format_daily_message(self, summary, hours=24):
        """Format the daily summary for Telegram"""
        from datetime import datetime
        
        if not summary:
            return "暂无热点信息"
        
        message = f"_过去{hours}小时的热门话题 Top {len(summary)}_\n\n"
        
        for i, trend in enumerate(summary, 1):
            title = trend['title']
            url = trend['url']
            count = trend['count']
            platform = trend['platform']
            
            # Escape special characters for Markdown
            title = title.replace('\\', '\\\\')
            title = title.replace('[', '\\[')
            title = title.replace(']', '\\]')
            title = title.replace('(', '\\(')
            title = title.replace(')', '\\)')
            
            # Add frequency indicator if appeared multiple times
            freq_indicator = f" 🔥×{count}" if count > 1 else ""
            platform_tag = f" _{platform}_" if platform else ""
            
            message += f"{i}. [{title}]({url}){freq_indicator}{platform_tag}\n"
        
        message += f"\n_数据来源: TrendMonitor 多平台聚合_"
        
        return message
