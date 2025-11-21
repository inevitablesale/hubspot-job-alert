"""Playwright browser helpers."""
from __future__ import annotations
from contextlib import asynccontextmanager
from playwright.async_api import async_playwright, BrowserContext
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

