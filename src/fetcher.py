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
            items = soup.select('.article-item-info')
            trends = []
            for item in items:
                a_tag = item.select_one('a.article-item-title')
                if a_tag:
                    title = a_tag.get_text().strip()
                    link = "https://36kr.com" + a_tag['href']
                    trends.append({'title': title, 'url': link})
            return trends[:15]
        except Exception as e:
            print(f"Error fetching 36Kr: {e}")
            return []

    def fetch_douyin(self):
        """Fetch Douyin Hot Search"""
        # 抖音热搜需要API，这里使用一个公开的聚合API
        url = "https://www.imsyy.top/api/hotlist/douyin"
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            data = response.json()
            trends = []
            if data.get('data'):
                for item in data['data'][:15]:
                    trends.append({
                        'title': item.get('title', ''),
                        'url': item.get('url', 'https://www.douyin.com')
                    })
            return trends
        except Exception as e:
            print(f"Error fetching Douyin: {e}")
            return []

    def fetch_bilibili(self):
        """Fetch Bilibili Hot Search"""
        url = "https://api.bilibili.com/x/web-interface/ranking/v2?rid=0&type=all"
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            data = response.json()
            trends = []
            if data.get('data') and data['data'].get('list'):
                for item in data['data']['list'][:15]:
                    trends.append({
                        'title': item.get('title', ''),
                        'url': f"https://www.bilibili.com/video/{item.get('bvid', '')}"
                    })
            return trends
        except Exception as e:
            print(f"Error fetching Bilibili: {e}")
            return []

    def fetch_tieba(self):
        """Fetch Tieba Hot List"""
        url = "https://tieba.baidu.com/hottopic/browse/topicList"
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            data = response.json()
            trends = []
            if data.get('data') and data['data'].get('bang_topic'):
                for item in data['data']['bang_topic']['topic_list'][:15]:
                    trends.append({
                        'title': item.get('topic_name', ''),
                        'url': item.get('topic_url', 'https://tieba.baidu.com')
                    })
            return trends
        except Exception as e:
            print(f"Error fetching Tieba: {e}")
            return []

    def fetch_toutiao(self):
        """Fetch Toutiao Hot List"""
        # 今日头条热榜需要使用聚合API
        url = "https://www.imsyy.top/api/hotlist/toutiao"
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            data = response.json()
            trends = []
            if data.get('data'):
                for item in data['data'][:15]:
                    trends.append({
                        'title': item.get('title', ''),
                        'url': item.get('url', 'https://www.toutiao.com')
                    })
            return trends
        except Exception as e:
            print(f"Error fetching Toutiao: {e}")
            return []

    def fetch_thepaper(self):
        """Fetch The Paper Hot List"""
        url = "https://www.thepaper.cn/api/www/v1/channel/getChannelNews?channelId=25950"
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            data = response.json()
            trends = []
            if data.get('data') and data['data'].get('list'):
                for item in data['data']['list'][:15]:
                    trends.append({
                        'title': item.get('name', ''),
                        'url': f"https://www.thepaper.cn/newsDetail_forward_{item.get('contId', '')}"
                    })
            return trends
        except Exception as e:
            print(f"Error fetching ThePaper: {e}")
            return []

    def fetch_hupu(self):
        """Fetch Hupu Hot List"""
        url = "https://bbs.hupu.com/all-gambia"
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')
            items = soup.select('.titlelink')
            trends = []
            for item in items[:15]:
                title = item.get_text().strip()
                link = "https://bbs.hupu.com" + item.get('href', '')
                if title:
                    trends.append({'title': title, 'url': link})
            return trends
        except Exception as e:
            print(f"Error fetching Hupu: {e}")
            return []

    def fetch_ithome(self):
        """Fetch IT Home Hot List"""
        url = "https://www.ithome.com/"
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')
            items = soup.select('.lst .title a')
            trends = []
            for item in items[:15]:
                title = item.get_text().strip()
                link = item.get('href', '')
                if not link.startswith('http'):
                    link = 'https://www.ithome.com' + link
                if title:
                    trends.append({'title': title, 'url': link})
            return trends
        except Exception as e:
            print(f"Error fetching ITHome: {e}")
            return []

    def fetch_v2ex(self):
        """Fetch V2EX Hot Topics"""
        url = "https://www.v2ex.com/api/topics/hot.json"
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            data = response.json()
            trends = []
            for item in data[:15]:
                trends.append({
                    'title': item.get('title', ''),
                    'url': f"https://www.v2ex.com/t/{item.get('id', '')}"
                })
            return trends
        except Exception as e:
            print(f"Error fetching V2EX: {e}")
            return []

    def fetch_douban(self):
        """Fetch Douban Hot Topics"""
        url = "https://www.douban.com/group/explore"
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            items = soup.select('.channel-item .title a')
            trends = []
            for item in items[:15]:
                title = item.get_text().strip()
                link = item.get('href', '')
                if title:
                    trends.append({'title': title, 'url': link})
            return trends
        except Exception as e:
            print(f"Error fetching Douban: {e}")
            return []

    def fetch_netease(self):
        """Fetch NetEase News Hot List"""
        url = "https://news.163.com/special/0001386F/rank_whole.html"
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.encoding = 'gbk'
            soup = BeautifulSoup(response.text, 'html.parser')
            items = soup.select('.tabContents tr td a')
            trends = []
            for item in items[:15]:
                title = item.get_text().strip()
                link = item.get('href', '')
                if title and link:
                    trends.append({'title': title, 'url': link})
            return trends
        except Exception as e:
            print(f"Error fetching NetEase: {e}")
            return []

    def fetch_ifeng(self):
        """Fetch Ifeng News Hot List"""
        url = "https://news.ifeng.com/"
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')
            items = soup.select('.box_01 a')
            trends = []
            for item in items[:15]:
                title = item.get_text().strip()
                link = item.get('href', '')
                if title and link.startswith('http'):
                    trends.append({'title': title, 'url': link})
            return trends
        except Exception as e:
            print(f"Error fetching Ifeng: {e}")
            return []

    def fetch_google_trends(self):
        """Fetch Google Trends (China)"""
        # 使用 Google Trends RSS
        url = "https://trends.google.com/trends/trendingsearches/daily/rss?geo=CN"
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.text, 'xml')
            items = soup.find_all('item')
            trends = []
            for item in items[:15]:
                title = item.find('title').get_text() if item.find('title') else ''
                link = item.find('link').get_text() if item.find('link') else ''
                if title:
                    trends.append({'title': title, 'url': link})
            return trends
        except Exception as e:
            print(f"Error fetching Google Trends: {e}")
            return []

    def fetch_reddit(self):
        """Fetch Reddit Popular (English)"""
        url = "https://www.reddit.com/r/popular.json?limit=15"
        try:
            response = requests.get(url, headers={**self.headers, 'User-Agent': 'TrendMonitor/1.0'}, timeout=10)
            data = response.json()
            trends = []
            if data.get('data') and data['data'].get('children'):
                for item in data['data']['children'][:15]:
                    post = item.get('data', {})
                    trends.append({
                        'title': post.get('title', ''),
                        'url': f"https://www.reddit.com{post.get('permalink', '')}"
                    })
            return trends
        except Exception as e:
            print(f"Error fetching Reddit: {e}")
            return []

    def fetch_all(self):
        """Fetch all trends from different platforms"""
        results = {}
        
        # 中文 + 国际平台
        platforms = {
            '微博': self.fetch_weibo,
            '知乎': self.fetch_zhihu,
            '百度': self.fetch_baidu,
            '36氪': self.fetch_36kr,
            '抖音': self.fetch_douyin,
            'B站': self.fetch_bilibili,
            '贴吧': self.fetch_tieba,
            '今日头条': self.fetch_toutiao,
            '澎湃新闻': self.fetch_thepaper,
            '虎扑': self.fetch_hupu,
            'IT之家': self.fetch_ithome,
            'V2EX': self.fetch_v2ex,
            '豆瓣': self.fetch_douban,
            '网易新闻': self.fetch_netease,
            '凤凰网': self.fetch_ifeng,
            'Google趋势': self.fetch_google_trends,
            'Reddit': self.fetch_reddit
        }
        
        for name, fetch_func in platforms.items():
            try:
                data = fetch_func()
                if data:
                    results[name] = data
            except Exception as e:
                print(f"Error fetching {name}: {e}")
        
        return results
