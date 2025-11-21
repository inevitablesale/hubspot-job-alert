"""Playwright browser helpers."""
from __future__ import annotations
import os
from contextlib import asynccontextmanager
from playwright.async_api import async_playwright, BrowserContext

# Ensure Playwright uses the same browser cache path at runtime that we used during
# postinstall. We keep the path inside the deployed bundle so the downloaded
# browsers are available at runtime instead of in ephemeral /tmp storage.
from config import PLAYWRIGHT_BROWSERS_PATH, REQUEST_TIMEOUT

os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", str(PLAYWRIGHT_BROWSERS_PATH))


@asynccontextmanager
async def browser_context() -> BrowserContext:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        context.set_default_timeout(REQUEST_TIMEOUT)
        try:
            yield context
        finally:
            await context.close()
            await browser.close()

