import os
from dotenv import load_dotenv

load_dotenv()

REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID", "")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET", "")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "PharmaSentinel:v1.0 (by /u/pharmasentinel_bot)")
REDDIT_USERNAME = os.getenv("REDDIT_USERNAME", "")
REDDIT_PASSWORD = os.getenv("REDDIT_PASSWORD", "")

TWITTER_API_KEY = os.getenv("TWITTER_API_KEY", "")

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./pharmasentinel.db")
SECRET_KEY = os.getenv("SECRET_KEY", "pharmasentinel-secret-key-change-in-prod")

SIGNAL_PRR_THRESHOLD = float(os.getenv("SIGNAL_PRR_THRESHOLD", "2.0"))
SIGNAL_MIN_REPORTS = int(os.getenv("SIGNAL_MIN_REPORTS", "3"))
