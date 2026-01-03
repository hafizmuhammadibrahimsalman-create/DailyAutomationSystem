gi# Daily News Intelligence System - Gemini AI Summarizer
# Uses Google Gemini API (Google One Pro) for intelligent summarization

import google.generativeai as genai
from typing import List, Dict, Optional
import json
import logging
from config import GEMINI_API_KEY, GEMINI_MODEL, GEMINI_FLASH, SUMMARIZER_PROMPT, INFOGRAPHIC_PROMPT, TOPICS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GeminiSummarizer:
    """AI-powered news summarizer using Google Gemini."""
    
    def __init__(self):
        if GEMINI_API_KEY and GEMINI_API_KEY != "YOUR_GEMINI_API_KEY_HERE":
            genai.configure(api_key=GEMINI_API_KEY)
            self.model = genai.GenerativeModel(GEMINI_MODEL)
            self.flash_model = genai.GenerativeModel(GEMINI_FLASH)
            self.enabled = True
            logger.info("✅ Gemini AI initialized successfully")
        else:
            self.enabled = False
            logger.warning("⚠️ Gemini API key not configured. Using basic summaries.")
    
    def create_intelligence_report(self, all_news: Dict[str, List[Dict]]) -> str:
        """Create a comprehensive intelligence report from all news."""
        
        if not self.enabled:
            return self._create_basic_report(all_news)
        
        try:
            # Prepare news data for AI
            news_json = json.dumps(all_news, indent=2, default=str)
            
            prompt = f"""{SUMMARIZER_PROMPT}

Today's collected news articles:
{news_json}

Create a comprehensive but CONCISE daily intelligence report. Format for WhatsApp:

1. Start with a greeting and today's date
2. For each topic category:
   - Use the topic emoji and name as header
   - List 2-3 most important items only
   - Use bullet points (•)
   - Include action items if any
   - Note: For Politics, create a brief infographic-style summary

3. End with:
   - 🎯 Key Takeaways (2-3 actionable insights)
   - 📊 Quick Stats (if relevant numbers)

IMPORTANT: 
- Be EXTREMELY selective - only truly important news
- Skip fluff, entertainment, and time-wasters
- Maximum 2000 characters total
- Make it scannable on mobile"""

            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            logger.error(f"Gemini error: {e}")
            return self._create_basic_report(all_news)
    
    def create_politics_infographic(self, politics_news: List[Dict]) -> str:
        """Create text-based infographic for political news."""
        
        if not self.enabled or not politics_news:
            return ""
        
        try:
            news_text = "\n".join([
                f"- {article['title']}: {article['description'][:100]}"
                for article in politics_news[:5]
            ])
            
            prompt = f"""{INFOGRAPHIC_PROMPT}

Political news to visualize:
{news_text}

Create a WhatsApp-friendly text infographic."""

            response = self.flash_model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            logger.error(f"Infographic error: {e}")
            return ""
    
    def filter_relevant_news(self, articles: List[Dict], topic_id: str) -> List[Dict]:
        """Use AI to filter only truly relevant news."""
        
        if not self.enabled or not articles:
            return articles[:3]
        
        try:
            topic_config = TOPICS.get(topic_id, {})
            filter_type = topic_config.get('filter', 'all')
            
            articles_text = "\n".join([
                f"{i+1}. {a['title']}" for i, a in enumerate(articles[:10])
            ])
            
            prompt = f"""From these {topic_config.get('name', 'news')} headlines, select ONLY the most important ones.

Filter criteria: {filter_type}
- beneficial: Must provide practical value or learning
- important: Major events only, skip routine news
- attention_worthy: Requires immediate attention or action
- very_valuable: Exceptional news only
- attention_required: Directly relevant to user's interests

Headlines:
{articles_text}

Return ONLY the numbers of selected headlines (e.g., "1, 3, 5")
Maximum 3 selections. Be VERY selective."""

            response = self.flash_model.generate_content(prompt)
            
            # Parse response to get selected indices
            selected_text = response.text.strip()
            selected_indices = []
            for num in selected_text.replace(',', ' ').split():
                try:
                    idx = int(num.strip()) - 1
                    if 0 <= idx < len(articles):
                        selected_indices.append(idx)
                except ValueError:
                    continue
            
            if selected_indices:
                return [articles[i] for i in selected_indices[:3]]
            return articles[:3]
            
        except Exception as e:
            logger.warning(f"Filter error: {e}")
            return articles[:3]
    
    def _create_basic_report(self, all_news: Dict[str, List[Dict]]) -> str:
        """Create a basic report without AI (fallback)."""
        from datetime import datetime
        
        lines = [
            f"📰 *Daily News Report*",
            f"📅 {datetime.now().strftime('%B %d, %Y')}",
            ""
        ]
        
        for topic_id, articles in all_news.items():
            if not articles:
                continue
                
            topic_config = TOPICS.get(topic_id, {})
            topic_name = topic_config.get('name', topic_id.title())
            
            lines.append(f"\n*{topic_name}*")
            
            for article in articles[:3]:
                title = article['title'][:80]
                lines.append(f"• {title}")
        
        lines.append("\n---")
        lines.append("_Powered by Daily News Intelligence_")
        
        return "\n".join(lines)


# Test the summarizer
if __name__ == "__main__":
    summarizer = GeminiSummarizer()
    
    # Test with sample data
    sample_news = {
        "ai": [
            {"title": "OpenAI releases GPT-5", "description": "Major AI breakthrough", "url": ""},
            {"title": "Google Gemini 2.0 announced", "description": "New features", "url": ""}
        ],
        "pakistan": [
            {"title": "Islamabad metro project update", "description": "New route", "url": ""}
        ]
    }
    
    print("🤖 Testing Gemini Summarizer...")
    report = summarizer.create_intelligence_report(sample_news)
    print("\n" + report)
