"""Central logging configuration."""
from __future__ import annotations
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import List

from config import DATA_DIR

LOG_FILE = DATA_DIR / "logs.txt"


def configure_logging() -> None:
    """Configure application-wide logging."""
    DATA_DIR.mkdir(exist_ok=True)
    handlers: List[logging.Handler] = [logging.StreamHandler()]
    try:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        file_handler = RotatingFileHandler(LOG_FILE, maxBytes=5_000_000, backupCount=1)
        handlers.append(file_handler)
    except OSError:
        # If filesystem not writable just skip file logging
        pass

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=handlers,
    )


def tail_logs(lines: int = 100) -> str:
    """Return the last N lines from the log file if available."""
    if not LOG_FILE.exists():
        return ""
    content = LOG_FILE.read_text().splitlines()
    return "\n".join(content[-lines:])

