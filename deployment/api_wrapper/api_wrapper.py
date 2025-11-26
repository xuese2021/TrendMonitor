from flask import Flask, jsonify, request
import requests
from bs4 import BeautifulSoup
import json
import time
from functools import wraps

app = Flask(__name__)

# 简单的内存缓存
cache_store = {}

def cache_for_minutes(minutes):
    """缓存装饰器（基于内存）"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            now = time.time()
            
            # 检查缓存
            if cache_key in cache_store:
                result, timestamp = cache_store[cache_key]
                if now - timestamp < minutes * 60:
                    print(f"Cache hit: {cache_key}")
                    return result
            
            # 执行函数
            result = func(*args, **kwargs)
            
            # 存入缓存
            cache_store[cache_key] = (result, now)
            
            # 清理过期缓存
            expired_keys = [k for k, (_, t) in cache_store.items() if now - t > minutes * 60]
            for k in expired_keys:
                del cache_store[k]
            
            return result
        return wrapper
    return decorator


@app.route('/')
def index():
    """首页"""
    return jsonify({
        'name': 'TrendMonitor API Wrapper',
        'version': '1.0.0',
        'endpoints': [
            '/health',
            '/api/weibo',
            '/api/zhihu',
            '/api/baidu'
        ]
    })


@app.route('/health')
def health():
    """健康检查"""
    return jsonify({
        'status': 'ok',
        'timestamp': time.time(),
        'cache_size': len(cache_store)
    })


@app.route('/api/weibo')
@cache_for_minutes(5)
def fetch_weibo():
    """代理微博热搜"""
    url = "https://s.weibo.com/top/summary"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        items = soup.select('td.td-02 a')
        trends = []
        
        for item in items[:15]:
            title = item.get_text().strip()
            href = item.get('href', '')
            link = "https://s.weibo.com" + href if href else url
            if title:
                trends.append({'title': title, 'url': link})
        
        return jsonify({
            'success': True,
            'data': trends,
            'count': len(trends),
            'timestamp': time.time()
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': time.time()
        }), 500


@app.route('/api/zhihu')
@cache_for_minutes(5)
def fetch_zhihu():
    """代理知乎热榜"""
    url = "https://www.zhihu.com/billboard"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        script = soup.find('script', id='js-initialData')
        
        if script:
            data = json.loads(script.string)
            hot_list = data.get('initialState', {}).get('topstory', {}).get('hotList', [])
            trends = []
            
            for item in hot_list[:15]:
                target = item.get('target', {})
                title_area = target.get('titleArea', {})
                link_info = target.get('link', {})
                
                title = title_area.get('text', '')
                link = link_info.get('url', '')
                
                if title:
                    trends.append({'title': title, 'url': link})
            
            return jsonify({
                'success': True,
                'data': trends,
                'count': len(trends),
                'timestamp': time.time()
            })
        
        return jsonify({
            'success': False,
            'error': 'No data found in page',
            'timestamp': time.time()
        }), 404
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': time.time()
        }), 500


@app.route('/api/baidu')
@cache_for_minutes(5)
def fetch_baidu():
    """代理百度热搜"""
    url = "https://top.baidu.com/board?tab=realtime"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        items = soup.select('.category-wrap_iQLoo')
        trends = []
        
        for item in items[:15]:
            title_div = item.select_one('.c-single-text-ellipsis')
            if title_div:
                title = title_div.get_text().strip()
                link_tag = item.select_one('a.img-wrapper_29V76')
                link = link_tag['href'] if link_tag and link_tag.get('href') else url
                if title:
                    trends.append({'title': title, 'url': link})
        
        return jsonify({
            'success': True,
            'data': trends,
            'count': len(trends),
            'timestamp': time.time()
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': time.time()
        }), 500


if __name__ == '__main__':
    # 本地开发运行
    app.run(host='0.0.0.0', port=8000, debug=True)
