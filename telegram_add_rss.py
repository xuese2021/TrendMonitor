"""
Telegram Bot - 一键添加 RSS 源到 TrendMonitor（全自动版）

使用方法：
1. 在 Telegram 找 @BotFather 创建新 Bot，获取 Token
2. 设置环境变量：
   - ADD_RSS_BOT_TOKEN: Telegram Bot Token
   - AUTO_GIT_PUSH: 设为 1 启用自动提交
3. 运行此脚本
4. 发送 RSS 链接给 Bot，自动添加并提交到 GitHub

消息格式：
- 直接发送 RSS 链接
- 或发送：名称|链接
"""

import os
import re
import requests
import time
import logging
import subprocess

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

# 配置
BOT_TOKEN = os.getenv('ADD_RSS_BOT_TOKEN', '')
CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'config', 'rss_feeds.txt')
PROJECT_DIR = os.path.dirname(__file__)
ALLOWED_USERS = os.getenv('ALLOWED_USERS', '').split(',')  # 允许的用户ID，逗号分隔
AUTO_GIT_PUSH = os.getenv('AUTO_GIT_PUSH', '1') == '1'  # 默认启用自动提交

def get_updates(offset=None):
    """获取 Telegram 更新"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
    params = {'timeout': 30}
    if offset:
        params['offset'] = offset
    
    try:
        resp = requests.get(url, params=params, timeout=35)
        return resp.json().get('result', [])
    except Exception as e:
        logger.error(f"获取更新失败: {e}")
        return []

def send_message(chat_id, text):
    """发送消息"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, json={
            'chat_id': chat_id,
            'text': text,
            'parse_mode': 'Markdown'
        })
    except Exception as e:
        logger.error(f"发送消息失败: {e}")

def extract_rss_info(text):
    """从消息中提取 RSS 信息"""
    text = text.strip()
    
    # 格式1：名称|链接
    if '|' in text:
        parts = text.split('|')
        if len(parts) >= 2:
            name = parts[0].strip()
            url = parts[1].strip()
            return name, url
    
    # 格式2：直接发送链接
    url_pattern = r'https?://[^\s]+'
    match = re.search(url_pattern, text)
    if match:
        url = match.group()
        # 从 URL 生成名称
        if 'rsshub' in url.lower():
            # 从 RSSHub URL 提取路由名称
            parts = url.replace('https://', '').replace('http://', '').split('/')
            if len(parts) > 1:
                name = '_'.join(parts[1:3])
            else:
                name = 'RSS源'
        else:
            # 从域名生成名称
            domain = url.split('/')[2] if len(url.split('/')) > 2 else 'RSS源'
            name = domain.replace('www.', '').split('.')[0]
        return name, url
    
    return None, None

def add_to_config(name, url):
    """添加 RSS 到配置文件"""
    # 检查是否已存在
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
            if url in content:
                return False, "该 RSS 源已存在"
    except FileNotFoundError:
        pass
    
    # 添加到文件末尾
    try:
        with open(CONFIG_FILE, 'a', encoding='utf-8') as f:
            f.write(f"\n{name}|{url}|true")
        return True, f"已添加: {name}"
    except Exception as e:
        return False, f"添加失败: {e}"

def git_commit_and_push(name):
    """自动 git commit 和 push"""
    if not AUTO_GIT_PUSH:
        return False, "自动提交未启用"
    
    try:
        # 切换到项目目录
        os.chdir(PROJECT_DIR)
        
        # git add
        result = subprocess.run(
            ['git', 'add', 'config/rss_feeds.txt'],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            return False, f"git add 失败: {result.stderr}"
        
        # git commit
        commit_msg = f"Add RSS: {name}"
        result = subprocess.run(
            ['git', 'commit', '-m', commit_msg],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            if 'nothing to commit' in result.stdout:
                return True, "无需提交（没有更改）"
            return False, f"git commit 失败: {result.stderr}"
        
        # git pull (避免冲突)
        subprocess.run(
            ['git', 'pull', '--rebase'],
            capture_output=True, text=True, timeout=60
        )
        
        # git push
        result = subprocess.run(
            ['git', 'push'],
            capture_output=True, text=True, timeout=60
        )
        if result.returncode != 0:
            return False, f"git push 失败: {result.stderr}"
        
        return True, "已自动提交到 GitHub"
    except subprocess.TimeoutExpired:
        return False, "Git 操作超时"
    except Exception as e:
        return False, f"Git 操作失败: {e}"

def validate_rss(url):
    """验证 RSS 是否可用"""
    try:
        resp = requests.get(url, timeout=10, headers={
            'User-Agent': 'Mozilla/5.0'
        })
        if resp.status_code == 200:
            content = resp.text.lower()
            if '<rss' in content or '<feed' in content or '<item' in content or '<entry' in content:
                return True, "RSS 有效"
        return False, f"HTTP {resp.status_code}"
    except Exception as e:
        return False, str(e)

def handle_message(message):
    """处理消息"""
    chat_id = message['chat']['id']
    user_id = str(message['from']['id'])
    text = message.get('text', '')
    
    # 检查权限（如果设置了允许用户列表）
    if ALLOWED_USERS and ALLOWED_USERS[0] and user_id not in ALLOWED_USERS:
        send_message(chat_id, "❌ 你没有权限使用此 Bot")
        return
    
    # 处理命令
    if text.startswith('/start'):
        auto_status = "✅ 已启用" if AUTO_GIT_PUSH else "❌ 未启用"
        send_message(chat_id, f"""🤖 *RSS 添加 Bot（全自动版）*

发送 RSS 链接，我会自动：
1. 验证 RSS 是否有效
2. 添加到配置文件
3. 自动提交到 GitHub

*自动提交状态：* {auto_status}

*支持格式：*
• 直接发送 RSS 链接
• `名称|链接` 格式

*示例：*
`https://rsshub.app/bilibili/popular/all`
`B站热门|https://rsshub.app/bilibili/popular/all`

*命令：*
/list - 查看当前源数量
/id - 查看你的用户ID""")
        return
    
    if text.startswith('/list'):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                lines = [l for l in f if l.strip() and not l.startswith('#') and '|' in l]
                enabled = len([l for l in lines if '|true' in l.lower()])
                send_message(chat_id, f"📋 当前配置: {len(lines)} 个源\n✅ 启用: {enabled} 个")
        except:
            send_message(chat_id, "❌ 无法读取配置文件")
        return
    
    if text.startswith('/id'):
        send_message(chat_id, f"你的用户 ID: `{user_id}`")
        return
    
    # 提取 RSS 信息
    name, url = extract_rss_info(text)
    
    if not url:
        send_message(chat_id, "❌ 未识别到 RSS 链接\n\n请发送有效的 RSS URL")
        return
    
    # 验证 RSS
    send_message(chat_id, f"🔍 验证中: {url[:50]}...")
    valid, msg = validate_rss(url)
    
    if not valid:
        send_message(chat_id, f"⚠️ RSS 验证失败: {msg}\n\n仍然添加？发送 `强制|{name}|{url}` 强制添加")
        return
    
    # 添加到配置
    success, result = add_to_config(name, url)
    
    if success:
        msg = f"""✅ *添加成功！*

📰 名称: {name}
🔗 链接: `{url}`
"""
        # 自动提交到 GitHub
        if AUTO_GIT_PUSH:
            send_message(chat_id, msg + "\n🔄 正在自动提交到 GitHub...")
            git_success, git_msg = git_commit_and_push(name)
            if git_success:
                send_message(chat_id, f"✅ {git_msg}\n\n🎉 下次运行时将自动抓取此源！")
            else:
                send_message(chat_id, f"⚠️ {git_msg}\n\n请手动提交")
        else:
            send_message(chat_id, msg + """
⚠️ 请手动提交到 GitHub:
```
git add config/rss_feeds.txt
git commit -m "Add {name}"
git push
```""")
    else:
        send_message(chat_id, f"❌ {result}")

def main():
    if not BOT_TOKEN:
        print("请设置环境变量 ADD_RSS_BOT_TOKEN")
        print("在 Telegram 找 @BotFather 创建 Bot 获取 Token")
        return
    
    logger.info("RSS 添加 Bot 启动...")
    logger.info(f"配置文件: {CONFIG_FILE}")
    
    offset = None
    while True:
        updates = get_updates(offset)
        
        for update in updates:
            offset = update['update_id'] + 1
            
            if 'message' in update:
                handle_message(update['message'])
        
        time.sleep(1)

if __name__ == '__main__':
    main()

