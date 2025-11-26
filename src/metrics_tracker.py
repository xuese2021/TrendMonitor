"""
Metrics tracker for monitoring scraping health
"""
import json
import os
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class MetricsTracker:
    def __init__(self, metrics_file='data/metrics.json'):
        self.metrics_file = metrics_file
        self.current_run = {
            'timestamp': datetime.now().isoformat(),
            'start_time': datetime.now(),
            'platforms': {},
            'total_platforms': 0,
            'success_count': 0,
            'failure_count': 0,
            'total_items': 0,
            'failed_platforms': []
        }
    
    def record_platform_attempt(self, platform_name):
        """Record platform fetch attempt"""
        self.current_run['total_platforms'] += 1
        self.current_run['platforms'][platform_name] = {
            'status': 'attempting',
            'start_time': datetime.now().isoformat()
        }
    
    def record_platform_success(self, platform_name, item_count, tier_used='http'):
        """Record successful platform fetch"""
        self.current_run['success_count'] += 1
        self.current_run['total_items'] += item_count
        self.current_run['platforms'][platform_name] = {
            'status': 'success',
            'items': item_count,
            'tier': tier_used,
            'timestamp': datetime.now().isoformat()
        }
    
    def record_platform_failure(self, platform_name, error_msg=''):
        """Record failed platform fetch"""
        self.current_run['failure_count'] += 1
        self.current_run['failed_platforms'].append(platform_name)
        self.current_run['platforms'][platform_name] = {
            'status': 'failed',
            'error': error_msg,
            'timestamp': datetime.now().isoformat()
        }
    
    def finalize(self):
        """Finalize metrics and calculate stats"""
        end_time = datetime.now()
        elapsed = (end_time - self.current_run['start_time']).total_seconds()
        
        self.current_run['execution_time'] = elapsed
        self.current_run['success_rate'] = (
            self.current_run['success_count'] / self.current_run['total_platforms']
            if self.current_run['total_platforms'] > 0 else 0
        )
        
        # Remove datetime objects for JSON serialization
        del self.current_run['start_time']
        
        return self.current_run
    
    def save_metrics(self):
        """Append metrics to file"""
        os.makedirs(os.path.dirname(self.metrics_file), exist_ok=True)
        
        # Load existing metrics
        metrics_history = []
        if os.path.exists(self.metrics_file):
            try:
                with open(self.metrics_file, 'r', encoding='utf-8') as f:
                    metrics_history = json.load(f)
            except Exception as e:
                logger.error(f"Failed to load metrics: {e}")
        
        # Append current run
        metrics_history.append(self.finalize())
        
        # Keep only last 100 runs
        if len(metrics_history) > 100:
            metrics_history = metrics_history[-100:]
        
        # Save
        try:
            with open(self.metrics_file, 'w', encoding='utf-8') as f:
                json.dump(metrics_history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Failed to save metrics: {e}")
    
    def get_summary(self):
        """Get human-readable summary"""
        total = self.current_run['total_platforms']
        success = self.current_run['success_count']
        failed = self.current_run['failure_count']
        items = self.current_run['total_items']
        
        # 避免除以零
        success_rate = (success / total * 100) if total > 0 else 0
        
        summary = f"""
📊 运行统计:
- 总平台数: {total}
- 成功: {success} ({success_rate:.1f}%)
- 失败: {failed}
- 总条目: {items}
"""
        if self.current_run['failed_platforms']:
            summary += f"- 失败平台: {', '.join(self.current_run['failed_platforms'])}\n"
        
        return summary
