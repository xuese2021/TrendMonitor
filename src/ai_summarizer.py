import os
import logging

logger = logging.getLogger(__name__)

class AISummarizer:
    """AI-powered summarizer using Google Gemini API"""
    
    def __init__(self):
        self.api_key = os.environ.get('GEMINI_API_KEY')
        self.enabled = bool(self.api_key)
        
        if self.enabled:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                # Use gemini-2.5-flash (latest, fastest, and free)
                self.model = genai.GenerativeModel('gemini-2.5-flash')
                logger.info("AI Summarizer initialized successfully")
            except ImportError:
                logger.error("google-generativeai package not installed. Run: pip install google-generativeai")
                self.enabled = False
            except Exception as e:
                logger.error(f"Failed to initialize AI Summarizer: {e}")
                self.enabled = False
        else:
            logger.info("AI Summarizer disabled (no GEMINI_API_KEY found)")
    
    def generate_summary(self, title, url=""):
        """
        Generate a brief summary for a news title
        
        Args:
            title: News title to summarize
            url: Optional URL (not currently used)
        
        Returns:
            str: Brief summary (2-3 sentences) or None if failed
        """
        if not self.enabled:
            return None
        
        try:
            prompt = f"""请为以下新闻标题生成一个简短的摘要(2-3句话，不超过80字):

标题: {title}

要求:
1. 突出核心信息和关键点
2. 适合自媒体人快速了解
3. 语言简洁、准确
4. 只输出摘要内容，不要其他说明"""
            
            response = self.model.generate_content(prompt)
            summary = response.text.strip()
            
            # Remove any markdown formatting
            summary = summary.replace('**', '').replace('*', '')
            
            logger.debug(f"Generated summary for: {title[:30]}...")
            return summary
            
        except Exception as e:
            logger.error(f"Error generating summary for '{title[:30]}...': {e}")
            return None
    
    def generate_summaries_batch(self, items, max_items=None):
        """
        Generate summaries for multiple items
        
        Args:
            items: List of dicts with 'title' and 'url' keys
            max_items: Maximum number of items to process (None = all)
        
        Returns:
            dict: Mapping of url -> summary
        """
        if not self.enabled:
            return {}
        
        summaries = {}
        items_to_process = items[:max_items] if max_items else items
        
        for item in items_to_process:
            summary = self.generate_summary(item['title'], item['url'])
            if summary:
                summaries[item['url']] = summary
        
        return summaries
