import requests
import time

class TelegramNotifier:
    def __init__(self, token, chat_id):
        self.token = token
        self.chat_id = chat_id
        self.api_url = f"https://api.telegram.org/bot{self.token}/sendMessage"

    def send_message(self, message):
        """Send message to Telegram, splitting if necessary"""
        if not message:
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
        for msg in messages:
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
            response = requests.post(self.api_url, json=payload, timeout=10)
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"Error sending message: {e}")
            return False

    def format_trends(self, trends_data):
        import datetime
        date_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        
        message = f"*🔥 Real-time Trends Monitor* \n_{date_str}_\n\n"
        
        for platform, items in trends_data.items():
            if not items:
                continue
            message += f"*{platform}*\n"
            for i, item in enumerate(items, 1):
                title = item['title'].replace('[', '(').replace(']', ')').replace('*', '\\*').replace('_', '\\_').replace('`', '\\`')
                url = item['url']
                # Telegram Markdown link: [text](url)
                message += f"{i}\. [{title}]({url})\n"
            message += "\n"
        return message
