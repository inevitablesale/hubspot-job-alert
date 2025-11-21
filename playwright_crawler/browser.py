"""Playwright browser helpers."""
from __future__ import annotations
import os
from contextlib import asynccontextmanager
from playwright.async_api import async_playwright, BrowserContext

# Ensure Playwright uses the same browser cache path at runtime that we used during
# postinstall. Render builds install browsers into /tmp/playwright-browsers, so we
# point the runtime lookup there if the environment is not already configured.
os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", "/tmp/playwright-browsers")
from config import REQUEST_TIMEOUT


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

