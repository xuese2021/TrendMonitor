import requests
import time
import logging
import re

logger = logging.getLogger(__name__)

class TelegramNotifier:
    def __init__(self, token, chat_id):
        self.token = token
        self.chat_id = chat_id
        self.api_url = f"https://api.telegram.org/bot{self.token}/sendMessage"

    def send_message(self, message):
        """Send message to Telegram, splitting if necessary"""
        if not message:
            logger.warning("Empty message, nothing to send")
            return False
            
        # Telegram message limit is 4096 characters. 
        # We'll split by newlines to avoid breaking markdown.
        max_length = 4000 # Leave some buffer
        
        messages = []
        if len(message) > max_length:
            current_msg = ""
            for line in message.split('\n'):
                if len(current_msg) + len(line) + 1 > max_length:
                    messages.append(current_msg)
                    current_msg = line + "\n"
                else:
                    current_msg += line + "\n"
            if current_msg:
                messages.append(current_msg)
        else:
            messages = [message]

        success = True
        for i, msg in enumerate(messages, 1):
            logger.info(f"Sending message part {i}/{len(messages)}")
            if not self._send_single_message(msg):
                success = False
            time.sleep(1) # Rate limiting
        return success

    def _send_single_message(self, text):
        payload = {
            'chat_id': self.chat_id,
            'text': text,
            'parse_mode': 'Markdown',
            'disable_web_page_preview': True
        }
        try:
            logger.debug(f"Sending to chat_id: {self.chat_id}")
            response = requests.post(self.api_url, json=payload, timeout=10)
            
            if response.status_code != 200:
                logger.error(f"Telegram HTTP error: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return False

            data = {}
            try:
                data = response.json()
            except Exception:
                logger.error("Telegram response is not JSON")
                return False

            if not data.get('ok', False):
                err_code = data.get('error_code')
                desc = data.get('description', '')
                logger.error(f"Telegram API error: {err_code} - {desc}")

                # 回退：如果是解析错误，改用纯文本发送
                if 'parse' in desc.lower() or 'entities' in desc.lower():
                    plain = self._to_plain_text(text)
                    logger.info("Retrying with plain text (no parse_mode)")
                    payload = {
                        'chat_id': self.chat_id,
                        'text': plain,
                        'disable_web_page_preview': True
                    }
                    retry_resp = requests.post(self.api_url, json=payload, timeout=10)
                    if retry_resp.status_code != 200:
                        logger.error(f"Telegram HTTP error on retry: {retry_resp.status_code}")
                        logger.error(f"Response: {retry_resp.text}")
                        return False
                    retry_data = {}
                    try:
                        retry_data = retry_resp.json()
                    except Exception:
                        logger.error("Telegram retry response is not JSON")
                        return False
                    if not retry_data.get('ok', False):
                        logger.error(f"Telegram API retry error: {retry_data.get('error_code')} - {retry_data.get('description')}")
                        return False
                    logger.info("Message sent successfully (plain text fallback)")
                    return True
                return False

            logger.info("Message sent successfully")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response text: {e.response.text}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending message: {e}")
            return False

    def _to_plain_text(self, text):
        # 将 Markdown 链接 [text](url) 转为两行：text\nurl
        def repl(m):
            t = m.group(1)
            u = m.group(2)
            return f"{t}\n{u}"

        text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", repl, text)
        # 去除粗体/斜体等标记
        text = text.replace('*', '')
        text = text.replace('_', '')
        return text

    def format_trends(self, trends_data):
        message = ""
        
        for platform, items in trends_data.items():
            if not items:
                continue
            for i, item in enumerate(items, 1):
                title = item['title']
                url = item['url']
                
                # 只转义会破坏 Markdown 链接的字符
                # 在链接文本中，只需要转义 [ ] ( ) 和 \
                title = title.replace('\\', '\\\\')  # 先转义反斜杠
                title = title.replace('[', '\\[')
                title = title.replace(']', '\\]')
                title = title.replace('(', '\\(')
                title = title.replace(')', '\\)')
                
                # Telegram Markdown link: [text](url)
                message += f"{i}. [{title}]({url})\n"
            message += "\n"
        
        logger.debug(f"Formatted message length: {len(message)} characters")
        return message
