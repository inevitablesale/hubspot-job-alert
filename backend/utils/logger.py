from backend.models import LogEntry
from backend.storage import memory_store


def log(level: str, message: str, context: dict | None = None):
    entry = LogEntry(
        timestamp=memory_store.now_iso(),
        level=level.upper(),
        message=message,
        context=context or {},
    )
    memory_store.append_log(entry)


def info(message: str, context: dict | None = None):
    log("INFO", message, context)


def warning(message: str, context: dict | None = None):
    log("WARNING", message, context)


def error(message: str, context: dict | None = None):
    log("ERROR", message, context)
