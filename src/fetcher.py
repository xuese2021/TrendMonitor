"""
TrendFetcher - 热点数据抓取器

策略优化版本：
1. 优先使用 RSS 源（最稳定，不易封禁）
2. 多 RSSHub 实例备份（主实例失败自动切换）
3. 请求重试机制（失败自动重试）
4. 随机延迟和 User-Agent 轮换
5. 预热请求（防止冷启动超时）
"""
import requests
from bs4 import BeautifulSoup
import os
import random
import time
import logging
import html

logger = logging.getLogger(__name__)

# User-Agent 池
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]

# 备用 RSSHub 镜像列表（主实例失败时使用）
BACKUP_RSSHUB_MIRRORS = [
    "https://rsshub.rssforever.com",
    "https://rsshub.feedly.com", 
    "https://hub.slarker.me",
    "https://rsshub.app",
]


class TrendFetcher:
    def __init__(self):
        # 主 RSSHub 实例
        self.rsshub_url = os.getenv('RSSHUB_URL', 'https://rsshub.app')
        self.backup_mirrors = BACKUP_RSSHUB_MIRRORS
        self.current_mirror_index = 0
        self.rsshub_healthy = True
        logger.info(f"Primary RSSHub: {self.rsshub_url}")
        
        # 预热请求（唤醒可能休眠的实例）
        self._warmup_rsshub()
    
    def _get_headers(self):
        """获取随机 User-Agent 的请求头"""
        return {
            'User-Agent': random.choice(USER_AGENTS),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        }
    
    def _random_delay(self, min_sec=0.5, max_sec=1.5):
        """添加随机延迟，降低封禁风险"""
        delay = random.uniform(min_sec, max_sec)
        time.sleep(delay)
    
    def _warmup_rsshub(self):
        """预热 RSSHub 实例（防止冷启动超时）"""
        try:
            logger.info("Warming up RSSHub instance...")
            response = requests.get(
                self.rsshub_url,
                headers=self._get_headers(),
                timeout=60  # 冷启动可能需要较长时间
            )
            if response.status_code == 200:
                logger.info("RSSHub warmup successful")
                self.rsshub_healthy = True
            else:
                logger.warning(f"RSSHub warmup returned {response.status_code}")
                self.rsshub_healthy = False
        except Exception as e:
            logger.warning(f"RSSHub warmup failed: {e}")
            self.rsshub_healthy = False
    
    def _get_rsshub_url(self):
        """获取当前可用的 RSSHub URL"""
        if self.rsshub_healthy:
            return self.rsshub_url
        # 使用备用镜像
        if self.current_mirror_index < len(self.backup_mirrors):
            return self.backup_mirrors[self.current_mirror_index]
        return self.rsshub_url
    
    def _switch_to_backup(self):
        """切换到下一个备用镜像"""
        self.rsshub_healthy = False
        if self.current_mirror_index < len(self.backup_mirrors) - 1:
            self.current_mirror_index += 1
            logger.info(f"Switching to backup mirror: {self.backup_mirrors[self.current_mirror_index]}")
    
    def _request_with_retry(self, url, max_retries=3, timeout=30):
        """带重试的请求"""
        last_error = None
        for attempt in range(max_retries):
            try:
                response = requests.get(
                    url,
                    headers=self._get_headers(),
                    timeout=timeout
                )
                if response.status_code == 200:
                    return response
                else:
                    logger.warning(f"Request returned {response.status_code}, attempt {attempt + 1}/{max_retries}")
            except requests.exceptions.Timeout:
                logger.warning(f"Request timeout, attempt {attempt + 1}/{max_retries}")
                last_error = "Timeout"
            except requests.exceptions.ConnectionError:
                logger.warning(f"Connection error, attempt {attempt + 1}/{max_retries}")
                last_error = "ConnectionError"
            except Exception as e:
                logger.warning(f"Request error: {e}, attempt {attempt + 1}/{max_retries}")
                last_error = str(e)
            
            # 重试前等待
            if attempt < max_retries - 1:
                time.sleep(2 * (attempt + 1))
        
        raise Exception(f"All {max_retries} attempts failed: {last_error}")
    
    # ===== 稳定的 API 平台 =====
    
    def fetch_bilibili(self):
        """获取 B站热门视频 - 使用官方 API，稳定可靠"""
        url = "https://api.bilibili.com/x/web-interface/ranking/v2?rid=0&type=all"
        try:
            response = requests.get(url, headers=self._get_headers(), timeout=15)
            data = response.json()
            trends = []
            if data.get('data') and data['data'].get('list'):
                for item in data['data']['list'][:10]:
                    trends.append({
                        'title': item.get('title', ''),
                        'url': f"https://www.bilibili.com/video/{item.get('bvid', '')}"
                    })
            return trends
        except Exception as e:
            logger.error(f"B站获取失败: {e}")
            return []
    
    # ===== RSS 源（最稳定）=====
    
    def _fetch_single_rss(self, name, url, use_backup=False):
        """获取单个 RSS 源，支持重试和备用镜像"""
        # 替换 rsshub.app 为当前实例
        current_rsshub = self._get_rsshub_url()
        if 'rsshub.app' in url:
            url = url.replace('https://rsshub.app', current_rsshub)
        
        try:
            response = self._request_with_retry(url, max_retries=2, timeout=30)
            
            soup = BeautifulSoup(response.content, 'xml')
            items = soup.find_all('item')
            if not items:
                items = soup.find_all('entry')
            
            trends = []
            for item in items[:10]:
                title_tag = item.find('title')
                link_tag = item.find('link')
                
                if title_tag:
                    title = html.unescape(title_tag.get_text().strip())
                    link = ''
                    if link_tag:
                        link = link_tag.get_text().strip() if link_tag.string else link_tag.get('href', '')
                    
                    if title:
                        trends.append({'title': title, 'url': link})
            
            return trends
            
        except Exception as e:
            # 如果主实例失败且还没尝试备用，切换到备用镜像重试
            if not use_backup and 'rsshub' in url.lower():
                self._switch_to_backup()
                return self._fetch_single_rss(name, url.replace(current_rsshub, 'https://rsshub.app'), use_backup=True)
            raise e
    
    def fetch_rss_feeds(self):
        """
        从配置文件获取 RSS 源
        增强版本：
        - 自动重试失败请求
        - 主实例失败自动切换备用镜像
        - 更长的超时时间
        """
        config_file = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
            'config', 'rss_feeds.txt'
        )
        
        if not os.path.exists(config_file):
            logger.warning("RSS config file not found")
            return {}
        
        results = {}
        success_count = 0
        fail_count = 0
        consecutive_failures = 0
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                lines = [l.strip() for l in f if l.strip() and not l.startswith('#')]
            
            for line in lines:
                parts = line.split('|')
                if len(parts) < 3:
                    continue
                    
                name = parts[0].strip()
                url = parts[1].strip()
                enabled = parts[2].strip().lower()
                
                if enabled != 'true':
                    continue
                
                # 如果连续失败超过 5 次，可能是网络问题，尝试切换镜像
                if consecutive_failures >= 5:
                    logger.warning("Too many consecutive failures, switching mirror...")
                    self._switch_to_backup()
                    consecutive_failures = 0
                
                try:
                    # 随机延迟，避免高频请求
                    self._random_delay(0.5, 1.5)
                    
                    trends = self._fetch_single_rss(name, url)
                    
                    if trends:
                        results[name] = trends
                        success_count += 1
                        consecutive_failures = 0
                        logger.info(f"RSS {name}: {len(trends)} items")
                        
                except Exception as e:
                    fail_count += 1
                    consecutive_failures += 1
                    logger.warning(f"RSS {name} failed: {str(e)[:50]}")
                    continue
                    
        except Exception as e:
            logger.error(f"Failed to read RSS config: {e}")
        
        logger.info(f"RSS complete: {success_count} success, {fail_count} failed")
        return results
    
    # ===== 聚合器 =====
    
    def fetch_all(self):
        """
        获取所有热点数据
        
        增强策略：
        1. 预热 RSSHub 实例（防止冷启动）
        2. RSS 源优先（最稳定）
        3. 自动重试和备用镜像切换
        4. B站官方 API 作为补充
        """
        results = {}
        
        logger.info("=" * 50)
        logger.info("Starting data fetch...")
        logger.info(f"Primary RSSHub: {self.rsshub_url}")
        logger.info(f"RSSHub healthy: {self.rsshub_healthy}")
        logger.info("=" * 50)
        
        # 1. 获取 B站数据（官方 API，非常稳定）
        try:
            self._random_delay(0.5, 1)
            bilibili_data = self.fetch_bilibili()
            if bilibili_data:
                results['B站'] = bilibili_data
                logger.info(f"Bilibili: {len(bilibili_data)} items")
        except Exception as e:
            logger.error(f"Bilibili failed: {e}")
        
        # 2. 获取 RSS 源数据（带重试和备用镜像）
        try:
            rss_data = self.fetch_rss_feeds()
            if rss_data:
                results.update(rss_data)
        except Exception as e:
            logger.error(f"RSS failed: {e}")
        
        logger.info("=" * 50)
        logger.info(f"Total: {len(results)} sources fetched")
        
        # 统计总条目数
        total_items = sum(len(items) for items in results.values())
        logger.info(f"Total items: {total_items}")
        logger.info("=" * 50)
        
        return results
