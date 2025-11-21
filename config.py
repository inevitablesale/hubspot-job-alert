"""Application configuration and constants."""
from pathlib import Path

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DOMAINS_FILE = DATA_DIR / "domains.json"
DATABASE_FILE = DATA_DIR / "jobs.db"
STATIC_DIR = BASE_DIR / "static"
FRONTEND_DIST = BASE_DIR / "frontend" / "dist"

DEFAULT_CRAWL_CONCURRENCY = 1
REQUEST_TIMEOUT = 15000
NAVIGATION_TIMEOUT = 20000

