import requests
from bs4 import BeautifulSoup
import time
import json

class TrendFetcher:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def fetch_weibo(self):
        """Fetch Weibo Hot Search"""
        url = "https://s.weibo.com/top/summary"
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            items = soup.select('td.td-02 a')
            trends = []
            for item in items:
                title = item.get_text().strip()
                link = "https://s.weibo.com" + item.get('href')
                # Filter out the "top" sticky item which often has no rank
                if title and not link.startswith("https://s.weibo.com/weibo?q=%23"): 
                     # Usually the top one is a promo, sometimes starts differently. 
                     # Real items usually have &Refer=top...
                     pass
                if title:
                    trends.append({'title': title, 'url': link})
            return trends[:15] 
        except Exception as e:
            print(f"Error fetching Weibo: {e}")
            return []

    def fetch_zhihu(self):
        """Fetch Zhihu Hot List"""
        url = "https://www.zhihu.com/billboard"
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            script = soup.find('script', id='js-initialData')
            if script:
                data = json.loads(script.string)
                hot_list = data['initialState']['topstory']['hotList']
                trends = []
                for item in hot_list:
                    title = item['target']['titleArea']['text']
                    link = item['target']['link']['url']
                    trends.append({'title': title, 'url': link})
                return trends[:15]
            return []
        except Exception as e:
            print(f"Error fetching Zhihu: {e}")
            return []

    def fetch_baidu(self):
        """Fetch Baidu Hot Search"""
        url = "https://top.baidu.com/board?tab=realtime"
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            # Baidu structure is complex, often class names change.
            # Look for the main container
            items = soup.select('.category-wrap_iQLoo')
            trends = []
            for item in items:
                title_div = item.select_one('.c-single-text-ellipsis')
                if title_div:
                    title = title_div.get_text().strip()
                    # Url is usually in a parent 'a' tag or similar
                    link_tag = item.select_one('a.img-wrapper_29V76')
                    link = link_tag['href'] if link_tag else url
                    trends.append({'title': title, 'url': link})
            return trends[:15]
        except Exception as e:
            print(f"Error fetching Baidu: {e}")
            return []

    def fetch_github(self):
        """Fetch GitHub Trending"""
        url = "https://github.com/trending"
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            items = soup.select('article.Box-row')
            trends = []
            for item in items:
                h2 = item.select_one('h2 a')
                if h2:
                    title = h2.get_text().strip().replace('\n', '').replace(' ', '')
                    link = "https://github.com" + h2['href']
                    desc_tag = item.select_one('p.col-9')
                    desc = desc_tag.get_text().strip() if desc_tag else ""
                    full_title = f"{title} - {desc}" if desc else title
                    trends.append({'title': full_title, 'url': link})
            return trends[:15]
        except Exception as e:
            print(f"Error fetching GitHub: {e}")
            return []

    def fetch_36kr(self):
        """Fetch 36Kr Hot List"""
        url = "https://36kr.com/hot-list/catalog"
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            # 36kr uses SSR but sometimes data is in script
            # Or simple selector
            items = soup.select('.article-item-info')
            trends = []
            for item in items:
                a_tag = item.select_one('a.article-item-title')
                if a_tag:
                    title = a_tag.get_text().strip()
                    link = "https://36kr.com" + a_tag['href']
                    trends.append({'title': title, 'url': link})
            
            # Fallback if HTML parsing fails (dynamic content)
            if not trends:
                # Try API approach if possible, but for now return empty or try another selector
                pass
                
            return trends[:15]
        except Exception as e:
            print(f"Error fetching 36Kr: {e}")
            return []

    def fetch_all(self):
        return {
            'Weibo': self.fetch_weibo(),
            'Zhihu': self.fetch_zhihu(),
            'Baidu': self.fetch_baidu(),
            'GitHub': self.fetch_github(),
            '36Kr': self.fetch_36kr()
        }
