# Daily News Intelligence System - Configuration
# Generated for: Hafiz | WhatsApp: +923300301917

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# =============================================================================
# USER CONFIGURATION
# =============================================================================

# Your WhatsApp number
WHATSAPP_NUMBER = os.getenv("WHATSAPP_NUMBER", "")

# Your Google Gemini API Key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# NewsAPI Key
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "YOUR_NEWSAPI_KEY_HERE")

# GNews API Key
GNEWS_API_KEY = os.getenv("GNEWS_API_KEY", "YOUR_GNEWS_KEY_HERE")

# =============================================================================
# YOUR INTERESTS & TOPICS (Customized for you)
# =============================================================================

TOPICS = {
    "ai": {
        "name": "🤖 AI & Machine Learning",
        "keywords": ["artificial intelligence", "machine learning", "ChatGPT", "Gemini", "OpenAI", "deep learning", "LLM", "neural network"],
        "priority": "HIGH",
        "include_all": True  # You want ALL AI news
    },
    "technology": {
        "name": "💻 Technology",
        "keywords": ["technology", "tech news", "software", "startup", "innovation", "free tools", "productivity"],
        "priority": "HIGH",
        "filter": "beneficial"  # Only beneficial tech news
    },
    "pakistan": {
        "name": "🇵🇰 Pakistan News",
        "keywords": ["Islamabad", "Taxila", "Karachi", "Pakistan", "Rawalpindi", "Punjab"],
        "priority": "HIGH",
        "cities": ["Islamabad", "Taxila", "Karachi", "Rawalpindi"],
        "filter": "important"  # Skip time-wasting news
    },
    "politics": {
        "name": "🏛️ Politics",
        "keywords": ["Pakistan politics", "government", "election", "PTI", "PML-N", "PPP", "Parliament"],
        "priority": "MEDIUM",
        "format": "infographic"  # Generate infographics
    },
    "business": {
        "name": "💼 Business",
        "keywords": ["business", "economy", "stock market", "investment", "PSX", "rupee", "startup funding"],
        "priority": "MEDIUM",
        "filter": "attention_worthy"  # Only important business news
    },
    "sports": {
        "name": "⚽ Sports",
        "keywords": ["Pakistan cricket", "PSL", "sports Pakistan", "Babar Azam", "hockey Pakistan"],
        "priority": "LOW",
        "filter": "very_valuable"  # Only very valuable sports news
    },
    "science": {
        "name": "🔬 Science",
        "keywords": ["science breakthrough", "research", "space", "health", "medicine", "discovery"],
        "priority": "MEDIUM",
        "filter": "beneficial"  # Only beneficial science
    },
    "ijt": {
        "name": "📚 Islami Jamiat Talaba",
        "keywords": ["Islami Jamiat Talaba", "IJT", "student union", "JI students"],
        "priority": "HIGH",
        "filter": "attention_required"
    }
}

# =============================================================================
# REPORT SETTINGS
# =============================================================================

# Time settings
REPORT_TIME = "21:00"  # 9:00 PM

# Maximum articles per category
MAX_ARTICLES_PER_TOPIC = 5

# Total maximum articles in report
MAX_TOTAL_ARTICLES = 25

# =============================================================================
# GEMINI AI SETTINGS (Using Google One Pro)
# =============================================================================

GEMINI_MODEL = "gemini-2.0-flash"  # Best available model
GEMINI_FLASH = "gemini-2.0-flash"  # Fast model for quick tasks

# System prompts for AI
SUMMARIZER_PROMPT = """You are an expert news analyst. Your job is to:
1. Analyze news articles and extract what's truly important
2. Filter out time-wasting or irrelevant news
3. Present information in a clear, concise manner
4. Highlight actionable insights
5. Focus on what benefits the user directly

User Profile:
- Location: Taxila/Islamabad area, Pakistan
- Interests: AI, Technology, Local News, Business, Science
- Association: Interested in IJT news
- Goal: Stay knowledgeable without wasting time

Be extremely selective. Quality over quantity."""

INFOGRAPHIC_PROMPT = """Create a text-based infographic for WhatsApp that visualizes the key political developments. Use:
- Emojis for visual appeal
- Clear hierarchy with headers
- Bullet points for key facts
- Numbers and statistics highlighted
- Keep it readable on mobile
Maximum 500 characters per section."""

# =============================================================================
# PATHS
# =============================================================================

BASE_DIR = Path(__file__).parent
CACHE_DIR = BASE_DIR / "cache"
LOG_FILE = BASE_DIR / "news_bot.log"

# Create cache directory if not exists
CACHE_DIR.mkdir(exist_ok=True)
