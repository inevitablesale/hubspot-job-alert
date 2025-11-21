"""Career page discovery heuristics."""
from __future__ import annotations
import logging
from urllib.parse import urljoin
from playwright.async_api import BrowserContext

logger = logging.getLogger(__name__)

CAREER_HINTS = ["career", "job", "join", "work", "opportun", "opening"]
CANDIDATE_PATHS = [
    "/careers",
    "/career",
    "/jobs",
    "/join-us",
    "/company/careers",
    "/about/careers",
]


async def discover_careers_page(context: BrowserContext, website: str) -> str | None:
    page = await context.new_page()
    try:
        logger.info("Scanning homepage %s for careers link", website)
        await page.goto(website, wait_until="domcontentloaded")
        anchors = await page.query_selector_all("a")
        scored: list[tuple[int, str]] = []
        for anchor in anchors:
            href = await anchor.get_attribute("href")
            text = (await anchor.inner_text() or "").lower()
            if not href:
                continue
            candidate = urljoin(website, href)
            for hint in CAREER_HINTS:
                if hint in text or hint in href.lower():
                    score = 2 if href.startswith("/") else 1
                    scored.append((score, candidate))
                    break
        for path in CANDIDATE_PATHS:
            scored.append((3, urljoin(website, path)))
        if not scored:
            return None
        scored.sort(key=lambda x: x[0], reverse=True)
        # de-duplicate while preserving score order
        seen: set[str] = set()
        for _, url in scored:
            if url in seen:
                continue
            seen.add(url)
            if url.startswith("http"):
                return url
        return None
    finally:
        await page.close()

