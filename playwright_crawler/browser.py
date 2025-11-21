"""Playwright browser helpers."""
from __future__ import annotations

import os
import subprocess
from contextlib import asynccontextmanager
from pathlib import Path

from playwright.async_api import BrowserContext, async_playwright

# Ensure Playwright uses the same browser cache path at runtime that we used during
# postinstall. We keep the path inside the deployed bundle so the downloaded
# browsers are available at runtime instead of in ephemeral /tmp storage.
from config import PLAYWRIGHT_BROWSERS_PATH, REQUEST_TIMEOUT

# Force the runtime to honor the bundled cache path even if another value is
# present in the environment (Render may set /tmp by default).
os.environ["PLAYWRIGHT_BROWSERS_PATH"] = str(PLAYWRIGHT_BROWSERS_PATH)


def _chromium_executable_exists() -> bool:
    """Return True if a Chromium binary exists in the configured cache path."""

    candidates = list(PLAYWRIGHT_BROWSERS_PATH.glob("chromium*/chrome-linux/*"))
    return any(Path(path).is_file() and os.access(path, os.X_OK) for path in candidates)


def ensure_browsers_installed() -> None:
    """Guarantee Chromium is available before attempting to launch.

    If the expected binaries are missing (e.g., cache wiped between deploy and
    runtime), run a one-time `playwright install chromium` using the configured
    cache path so crawls can proceed instead of failing immediately.
    """

    if _chromium_executable_exists():
        return

    subprocess.run(
        ["python", "-m", "playwright", "install", "chromium"],
        check=True,
        env={**os.environ, "PLAYWRIGHT_BROWSERS_PATH": str(PLAYWRIGHT_BROWSERS_PATH)},
    )


@asynccontextmanager
async def browser_context() -> BrowserContext:
    ensure_browsers_installed()
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        context.set_default_timeout(REQUEST_TIMEOUT)
        try:
            yield context
        finally:
            await context.close()
            await browser.close()

