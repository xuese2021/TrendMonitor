import requests
import time
import logging

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
                logger.error(f"Telegram API error: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return False
            
            response.raise_for_status()
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

    def format_trends(self, trends_data):
        import datetime
        date_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        
        message = f"*🔥 实时热点监控* \n_{date_str}_\n\n"
        
        for platform, items in trends_data.items():
            if not items:
                continue
            message += f"*{platform}*\n"
            for i, item in enumerate(items, 1):
                # 更严格的 Markdown 转义
                title = item['title']
                # 转义所有 Markdown 特殊字符
                for char in ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']:
                    title = title.replace(char, '\\' + char)
                
                url = item['url']
                # Telegram Markdown link: [text](url)
                message += f"{i}\\. [{title}]({url})\n"
            message += "\n"
        
        logger.debug(f"Formatted message length: {len(message)} characters")
        return message
