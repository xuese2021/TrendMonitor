import requests
from bs4 import BeautifulSoup
import json
import os

class TrendFetcher:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        # 自建 RSSHub 实例配置
        self.rsshub_url = os.getenv('RSSHUB_URL', 'https://rsshub.app')
        # API Wrapper 地址配置（可选）
        self.api_wrapper_url = os.getenv('API_WRAPPER_URL', '')
        self.use_api_wrapper = bool(self.api_wrapper_url)
        
        print(f"RSSHub URL: {self.rsshub_url}")
        if self.use_api_wrapper:
            print(f"API Wrapper URL: {self.api_wrapper_url}")
    
    def check_server_health(self, url):
        """检查服务器健康状态"""
        try:
            response = requests.get(f"{url}/health", timeout=5)
            return response.status_code == 200
        except Exception as e:
            print(f"Health check failed for {url}: {e}")
            return False

    # ------------------- Existing Chinese platforms -------------------
    def fetch_weibo(self):
        """Fetch Weibo Hot Search - 优先使用 API Wrapper"""
        # 尝试使用 API Wrapper
        if self.use_api_wrapper and self.check_server_health(self.api_wrapper_url):
            try:
                response = requests.get(f"{self.api_wrapper_url}/api/weibo", timeout=15)
                data = response.json()
                if data.get('success') and data.get('data'):
                    print(f"✓ Weibo: 使用 API Wrapper 成功 ({data.get('count')} 条)")
                    return data.get('data', [])
            except Exception as e:
                print(f"API Wrapper 失败，回退到直接抓取: {e}")
        
        # 回退到直接抓取
        url = "https://s.weibo.com/top/summary"
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            items = soup.select('td.td-02 a')
            trends = []
            for item in items:
                title = item.get_text().strip()
                link = "https://s.weibo.com" + item.get('href')
                if title and not link.startswith("https://s.weibo.com/weibo?q=%23"):
                    pass
                if title:
                    trends.append({'title': title, 'url': link})
            print(f"✓ Weibo: 直接抓取成功 ({len(trends[:15])} 条)")
            return trends[:15]
        except Exception as e:
            print(f"Error fetching Weibo: {e}")
            return []

    def fetch_zhihu(self):
        """Fetch Zhihu Hot List - 优先使用 API Wrapper"""
        # 尝试使用 API Wrapper
        if self.use_api_wrapper and self.check_server_health(self.api_wrapper_url):
            try:
                response = requests.get(f"{self.api_wrapper_url}/api/zhihu", timeout=15)
                data = response.json()
                if data.get('success') and data.get('data'):
                    print(f"✓ Zhihu: 使用 API Wrapper 成功 ({data.get('count')} 条)")
                    return data.get('data', [])
            except Exception as e:
                print(f"API Wrapper 失败，回退到直接抓取: {e}")
        
        # 回退到直接抓取
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
                print(f"✓ Zhihu: 直接抓取成功 ({len(trends[:15])} 条)")
                return trends[:15]
            return []
        except Exception as e:
            print(f"Error fetching Zhihu: {e}")
            return []

    def fetch_baidu(self):
        """Fetch Baidu Hot Search - 优先使用 API Wrapper"""
        # 尝试使用 API Wrapper
        if self.use_api_wrapper and self.check_server_health(self.api_wrapper_url):
            try:
                response = requests.get(f"{self.api_wrapper_url}/api/baidu", timeout=15)
                data = response.json()
                if data.get('success') and data.get('data'):
                    print(f"✓ Baidu: 使用 API Wrapper 成功 ({data.get('count')} 条)")
                    return data.get('data', [])
            except Exception as e:
                print(f"API Wrapper 失败，回退到直接抓取: {e}")
        
        # 回退到直接抓取
        url = "https://top.baidu.com/board?tab=realtime"
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            items = soup.select('.category-wrap_iQLoo')
            trends = []
            for item in items:
                title_div = item.select_one('.c-single-text-ellipsis')
                if title_div:
                    title = title_div.get_text().strip()
                    link_tag = item.select_one('a.img-wrapper_29V76')
                    link = link_tag['href'] if link_tag else url
                    trends.append({'title': title, 'url': link})
            print(f"✓ Baidu: 直接抓取成功 ({len(trends[:15])} 条)")
            return trends[:15]
        except Exception as e:
            print(f"Error fetching Baidu: {e}")
            return []

    def fetch_douyin(self):
        """Fetch Douyin Hot Search"""
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
                        'title': item.get('title', ''),
                        'url': f"https://www.thepaper.cn{item.get('url', '')}"
                    })
            return trends
        except Exception as e:
            print(f"Error fetching The Paper: {e}")
            return []

    # ------------------- Additional Chinese platforms -------------------
    def fetch_hupu(self):
        """Fetch Hupu Hot Topics"""
        url = "https://rsshub.app/hupu/all"
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
            print(f"Error fetching Hupu: {e}")
            return []

    def fetch_ithome(self):
        """Fetch IT之家 Hot News"""
        url = "https://rsshub.app/ithome/news"
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
            print(f"Error fetching IT之家: {e}")
            return []

    def fetch_v2ex(self):
        """Fetch V2EX Hot Topics"""
        url = "https://rsshub.app/v2ex/topics/hot"
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
            print(f"Error fetching V2EX: {e}")
            return []

    def fetch_douban(self):
        """Fetch Douban Hot Topics"""
        url = "https://rsshub.app/douban/group"
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
            print(f"Error fetching Douban: {e}")
            return []

    def fetch_netease(self):
        """Fetch NetEase News"""
        url = "https://rsshub.app/netease/news"
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
            print(f"Error fetching NetEase: {e}")
            return []

    def fetch_ifeng(self):
        """Fetch Ifeng News"""
        url = "https://rsshub.app/ifeng/news"
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
            print(f"Error fetching Ifeng: {e}")
            return []

    # ------------------- International platforms -------------------
    def fetch_google_trends(self):
        """Fetch Google Trends (China)"""
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
        """Fetch Reddit Popular"""
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

    def fetch_yahoo_news(self):
        """Fetch Yahoo News Top Stories"""
        url = "https://news.yahoo.com/rss/"
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
            print(f"Error fetching Yahoo News: {e}")
            return []

    def fetch_hackernews(self):
        """Fetch Hacker News Top Stories"""
        url = "https://hacker-news.firebaseio.com/v0/topstories.json"
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            story_ids = response.json()[:15]
            trends = []
            for story_id in story_ids:
                story_url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
                story_response = requests.get(story_url, headers=self.headers, timeout=5)
                story = story_response.json()
                if story and story.get('title'):
                    trends.append({
                        'title': story.get('title', ''),
                        'url': story.get('url', f"https://news.ycombinator.com/item?id={story_id}")
                    })
            return trends
        except Exception as e:
            print(f"Error fetching Hacker News: {e}")
            return []

    def fetch_producthunt(self):
        """Fetch Product Hunt Top Products"""
        url = "https://www.producthunt.com/"
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            items = soup.select('[data-test="post-item"] a[href^="/posts/"]')
            trends = []
            for item in items[:15]:
                title = item.get_text().strip()
                link = "https://www.producthunt.com" + item.get('href', '')
                if title:
                    trends.append({'title': title, 'url': link})
            return trends
        except Exception as e:
            print(f"Error fetching Product Hunt: {e}")
            return []

    def fetch_techcrunch(self):
        """Fetch TechCrunch Latest News"""
        url = "https://techcrunch.com/feed/"
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
            print(f"Error fetching TechCrunch: {e}")
            return []

    def fetch_bbc(self):
        """Fetch BBC News Top Stories"""
        url = "http://feeds.bbci.co.uk/news/rss.xml"
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
            print(f"Error fetching BBC: {e}")
            return []

    def fetch_theverge(self):
        """Fetch The Verge Latest News"""
        url = "https://www.theverge.com/rss/index.xml"
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
            print(f"Error fetching The Verge: {e}")
            return []

    # ------------------- RSS Feed Support -------------------
    def fetch_rss_feeds(self):
        """Fetch RSS feeds from config file"""
        import html
        config_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config', 'rss_feeds.txt')
        if not os.path.exists(config_file):
            print("RSS配置文件不存在，跳过RSS抓取")
            return {}
        results = {}
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    parts = line.split('|')
                    if len(parts) < 3:
                        continue
                    name, url, enabled = parts[0].strip(), parts[1].strip(), parts[2].strip().lower()
                    if enabled != 'true':
                        continue
                    
                    # 替换 rsshub.app 为自建实例
                    if 'rsshub.app' in url:
                        url = url.replace('https://rsshub.app', self.rsshub_url)
                        print(f"✓ {name}: 使用自建 RSSHub 实例")
                    
                    try:
                        response = requests.get(url, headers=self.headers, timeout=15)
                        # Use content instead of text for better encoding handling
                        soup = BeautifulSoup(response.content, 'xml')
                        items = soup.find_all('item')
                        if not items:
                            items = soup.find_all('entry')
                        trends = []
                        for item in items[:10]:
                            title_tag = item.find('title')
                            link_tag = item.find('link')
                            if title_tag:
                                # Decode HTML entities to fix garbled text
                                title = html.unescape(title_tag.get_text().strip())
                                if link_tag:
                                    link = link_tag.get_text().strip() if link_tag.string else link_tag.get('href', '')
                                else:
                                    link = ''
                                if title:
                                    trends.append({'title': title, 'url': link})
                        if trends:
                            results[name] = trends
                            print(f"成功抓取RSS: {name} ({len(trends)}条)")
                    except Exception as e:
                        print(f"抓取RSS失败 {name}: {e}")
                        continue
        except Exception as e:
            print(f"读取RSS配置文件失败: {e}")
        return results


    # ------------------- Aggregator -------------------
    def fetch_all(self):
        """Fetch all trends from different platforms"""
        results = {}
        platforms = {
            # 中文主流平台
            '微博': self.fetch_weibo,
            '知乎': self.fetch_zhihu,
            '百度': self.fetch_baidu,
            '抖音': self.fetch_douyin,
            'B站': self.fetch_bilibili,
            '贴吧': self.fetch_tieba,
            '今日头条': self.fetch_toutiao,
            # 中文科技/商业媒体
            # '36氪': self.fetch_36kr, # Method missing
            # '虎嗅': self.fetch_hupu, # Incorrect mapping and method missing
            # '钛媒体': self.fetch_tmtpost, # Method missing
            # '爱范儿': self.fetch_ifanr, # Method missing
            # '少数派': self.fetch_sspai, # Method missing
            'IT之家': self.fetch_ithome,
            # 中文新闻媒体
            '澎湃新闻': self.fetch_thepaper,
            '网易新闻': self.fetch_netease,
            '凤凰网': self.fetch_ifeng,
            # 中文社区
            '虎扑': self.fetch_hupu,
            'V2EX': self.fetch_v2ex,
            '豆瓣': self.fetch_douban,
            # 国际平台
            # 'Google趋势': self.fetch_google_trends,
            # 'Reddit': self.fetch_reddit,
            # 'Yahoo新闻': self.fetch_yahoo_news,
            # 'Hacker News': self.fetch_hackernews,
            # 'Product Hunt': self.fetch_producthunt,
            # 'TechCrunch': self.fetch_techcrunch,
            # 'BBC News': self.fetch_bbc,
            # 'The Verge': self.fetch_theverge
        }
        for name, func in platforms.items():
            try:
                data = func()
                if data:
                    results[name] = data
            except Exception as e:
                print(f"Error fetching {name}: {e}")
        # RSS feeds
        try:
            rss = self.fetch_rss_feeds()
            if rss:
                results.update(rss)
        except Exception as e:
            print(f"Error fetching RSS feeds: {e}")
        return results
