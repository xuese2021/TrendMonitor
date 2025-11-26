"""
TrendFetcher - 热点数据抓取器

策略优化版本：
1. 优先使用 RSS 源（最稳定，不易封禁）
2. 只保留少量稳定的官方 API
3. 添加随机延迟和 User-Agent 轮换
4. 带重试机制
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


class TrendFetcher:
    def __init__(self):
        # 自建 RSSHub 实例配置（可选）
        self.rsshub_url = os.getenv('RSSHUB_URL', 'https://rsshub.app')
        logger.info(f"RSSHub URL: {self.rsshub_url}")
    
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
    
    def fetch_rss_feeds(self):
        """
        从配置文件获取 RSS 源
        这是最稳定的数据获取方式，不易被封禁
        """
        config_file = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
            'config', 'rss_feeds.txt'
        )
        
        if not os.path.exists(config_file):
            logger.warning("RSS配置文件不存在")
            return {}
        
        results = {}
        success_count = 0
        fail_count = 0
        
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
                
                # 替换 rsshub.app 为自建实例
                if 'rsshub.app' in url:
                    url = url.replace('https://rsshub.app', self.rsshub_url)
                
                try:
                    # 随机延迟，避免高频请求
                    self._random_delay(0.3, 1.0)
                    
                    response = requests.get(
                        url, 
                        headers=self._get_headers(), 
                        timeout=20
                    )
                    
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
                    
                    if trends:
                        results[name] = trends
                        success_count += 1
                        logger.info(f"RSS {name}: {len(trends)} 条")
                        
                except Exception as e:
                    fail_count += 1
                    logger.warning(f"RSS {name} 失败: {str(e)[:50]}")
                    continue
                    
        except Exception as e:
            logger.error(f"读取RSS配置失败: {e}")
        
        logger.info(f"RSS完成: 成功 {success_count}, 失败 {fail_count}")
        return results
    
    # ===== 聚合器 =====
    
    def fetch_all(self):
        """
        获取所有热点数据
        
        优化策略：
        1. RSS 源优先（最稳定）
        2. 只保留 B站 API（官方接口稳定）
        3. 禁用高风险直接抓取
        """
        results = {}
        
        # 1. 获取 B站数据（官方 API）
        try:
            self._random_delay(0.5, 1)
            bilibili_data = self.fetch_bilibili()
            if bilibili_data:
                results['B站'] = bilibili_data
                logger.info(f"B站: {len(bilibili_data)} 条")
        except Exception as e:
            logger.error(f"B站失败: {e}")
        
        # 2. 获取 RSS 源数据（最稳定）
        try:
            rss_data = self.fetch_rss_feeds()
            if rss_data:
                results.update(rss_data)
        except Exception as e:
            logger.error(f"RSS失败: {e}")
        
        logger.info(f"总计获取 {len(results)} 个数据源")
        return results
