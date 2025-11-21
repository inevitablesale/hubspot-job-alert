"""Application configuration and constants."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).parent


def resolve_data_dir() -> Path:
    """Return a writable data directory.

    Render's persistent volume is mounted at /data, but if the process lacks
    permission to create that directory (e.g., during local runs or misconfigured
    environments) we gracefully fall back to a project-local ./data directory so
    the server can start instead of crashing.
    """

    preferred = Path(os.getenv("DATA_DIR", "/data"))
    fallback = BASE_DIR / "data"

    for candidate in (preferred, fallback):
        try:
            candidate.mkdir(parents=True, exist_ok=True)
            if os.access(candidate, os.W_OK):
                return candidate
        except PermissionError:
            continue

    # As a last resort, use BASE_DIR without creating a subfolder.
    return BASE_DIR


# Persist the crawl database on Render's /data volume when available.
DATA_DIR = resolve_data_dir()

# DOMAINS_FILE must come from the deployment secret (defaulting to Render's /etc/secrets/DOMAINS_FILE).
DOMAINS_FILE = Path(os.getenv("DOMAINS_FILE", "/etc/secrets/DOMAINS_FILE"))
DATABASE_FILE = DATA_DIR / "jobs.db"
STATIC_DIR = BASE_DIR / "static"
FRONTEND_DIST = BASE_DIR / "frontend" / "dist"
PLAYWRIGHT_BROWSERS_PATH = Path(
    os.getenv("PLAYWRIGHT_BROWSERS_PATH", BASE_DIR / ".playwright-browsers")
)

DEFAULT_CRAWL_CONCURRENCY = 1
REQUEST_TIMEOUT = 15000
NAVIGATION_TIMEOUT = 20000

