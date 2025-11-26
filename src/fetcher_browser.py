"""
Browser-based fetchers using DrissionPage for sites that require JavaScript rendering
"""
from DrissionPage import ChromiumPage, ChromiumOptions
import logging
import time

logger = logging.getLogger(__name__)

class BrowserFetcher:
    """Browser-based fetcher for JS-heavy sites"""
    
    def __init__(self):
        self._page = None
        self._init_browser()
    
    def _init_browser(self):
        """Initialize browser with headless mode and anti-detection"""
        try:
            options = ChromiumOptions()
            options.headless(True)  # Run in headless mode
            options.set_argument('--no-sandbox')
            options.set_argument('--disable-dev-shm-usage')
            options.set_argument('--disable-blink-features=AutomationControlled')
            options.set_argument('--disable-gpu')
            options.set_argument('--window-size=1920,1080')
            options.set_user_agent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            
            self._page = ChromiumPage(addr_or_opts=options)
            
            # Anti-detection: Hide webdriver flag
            self._page.run_js('''
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            ''')
            
            logger.info("Browser initialized successfully with anti-detection")
        except Exception as e:
            logger.error(f"Failed to initialize browser: {e}")
            self._page = None
    
    def close(self):
        """Close browser"""
        if self._page:
            try:
                self._page.quit()
            except Exception as e:
                logger.error(f"Error closing browser: {e}")
    
    def fetch_weibo_browser(self):
        """Fetch Weibo using browser automation"""
        if not self._page:
            logger.error("Browser not initialized")
            return []
        
        url = "https://s.weibo.com/top/summary"
        try:
            logger.info("Fetching Weibo with browser...")
            self._page.get(url, timeout=15)
            time.sleep(2)  # Wait for JS to load
            
            # Use DrissionPage's simplified syntax
            trends = []
            items = self._page.eles('tag:td@class=td-02')
            
            for item in items[:15]:
                try:
                    link_ele = item.ele('tag:a', timeout=1)
                    if link_ele:
                        title = link_ele.text.strip()
                        href = link_ele.attr('href')
                        if title and href:
                            full_url = f"https://s.weibo.com{href}" if not href.startswith('http') else href
                            trends.append({'title': title, 'url': full_url})
                except Exception:
                    continue
            
            logger.info(f"✓ Weibo (Browser): {len(trends)} items")
            return trends
            
        except Exception as e:
            logger.error(f"Browser fetch Weibo failed: {e}")
            return []
    
    def fetch_zhihu_browser(self):
        """Fetch Zhihu using browser automation"""
        if not self._page:
            logger.error("Browser not initialized")
            return []
        
        url = "https://www.zhihu.com/billboard"
        try:
            logger.info("Fetching Zhihu with browser...")
            self._page.get(url, timeout=15)
            time.sleep(3)  # Wait for JS to load
            
            trends = []
            # Zhihu's hot list items
            items = self._page.eles('tag:div@class^=HotItem-content')
            
            for item in items[:15]:
                try:
                    title_ele = item.ele('tag:h2', timeout=1)
                    link_ele = item.ele('tag:a', timeout=1)
                    
                    if title_ele and link_ele:
                        title = title_ele.text.strip()
                        href = link_ele.attr('href')
                        if title and href:
                            full_url = href if href.startswith('http') else f"https://www.zhihu.com{href}"
                            trends.append({'title': title, 'url': full_url})
                except Exception:
                    continue
            
            logger.info(f"✓ Zhihu (Browser): {len(trends)} items")
            return trends
            
        except Exception as e:
            logger.error(f"Browser fetch Zhihu failed: {e}")
            return []
    
    def fetch_baidu_browser(self):
        """Fetch Baidu using browser automation"""
        if not self._page:
            logger.error("Browser not initialized")
            return []
        
        url = "https://top.baidu.com/board?tab=realtime"
        try:
            logger.info("Fetching Baidu with browser...")
            self._page.get(url, timeout=15)
            time.sleep(2)  # Wait for JS to load
            
            trends = []
            # Baidu's hot search items
            items = self._page.eles('tag:div@class^=category-wrap')
            
            for item in items[:15]:
                try:
                    title_ele = item.ele('tag:div@class=c-single-text-ellipsis', timeout=1)
                    link_ele = item.ele('tag:a', timeout=1)
                    
                    if title_ele:
                        title = title_ele.text.strip()
                        href = link_ele.attr('href') if link_ele else url
                        if title:
                            trends.append({'title': title, 'url': href})
                except Exception:
                    continue
            
            logger.info(f"✓ Baidu (Browser): {len(trends)} items")
            return trends
            
        except Exception as e:
            logger.error(f"Browser fetch Baidu failed: {e}")
            return []

# Singleton instance
_browser_fetcher = None

def get_browser_fetcher():
    """Get or create browser fetcher singleton"""
    global _browser_fetcher
    if _browser_fetcher is None:
        _browser_fetcher = BrowserFetcher()
    return _browser_fetcher

def cleanup_browser():
    """Cleanup browser instance"""
    global _browser_fetcher
    if _browser_fetcher:
        _browser_fetcher.close()
        _browser_fetcher = None
