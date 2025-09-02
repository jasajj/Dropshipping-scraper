import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

META_ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN", "")
META_API_VERSION = os.getenv("META_API_VERSION", "v23.0")
DB_URL = os.getenv("DB_URL", "sqlite:///./ads.db")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
USER_AGENT = "dropship-scraper/1.0 (+https://example.com)"

