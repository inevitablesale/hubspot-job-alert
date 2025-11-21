"""Job listing extraction."""
from __future__ import annotations
import logging
from datetime import datetime
from typing import List, Set
from urllib.parse import urljoin
from playwright.async_api import BrowserContext

from models import Job

logger = logging.getLogger(__name__)

JOB_KEYWORDS = [
    "engineer",
    "developer",
    "consultant",
    "designer",
    "manager",
    "strategist",
    "specialist",
    "architect",
    "sales",
    "marketing",
]


async def extract_jobs(context: BrowserContext, careers_url: str, domain_id: int, domain_title: str, domain_website: str) -> List[Job]:
    """Discover and scrape job detail pages from a careers listing."""

    page = await context.new_page()
    logger.info("Opening careers page %s", careers_url)
    await page.goto(careers_url, wait_until="domcontentloaded")

    candidates: Set[str] = set()
    candidates.update(await _ats_job_links(page, careers_url))
    candidates.update(await _keyword_job_links(page, careers_url))

    if not candidates:
        logger.info("No candidate job links discovered at %s", careers_url)
        await page.close()
        return []

    logger.info("Discovered %d candidate job links at %s", len(candidates), careers_url)
    jobs: List[Job] = []
    for url in candidates:
        try:
            job = await scrape_job_detail(context, url, domain_id, domain_title, domain_website)
            if job:
                jobs.append(job)
        except Exception as exc:  # noqa: BLE001
            logger.error("Failed to scrape %s: %s", url, exc)
    await page.close()
    return jobs


async def scrape_job_detail(context: BrowserContext, job_url: str, domain_id: int, domain_title: str, domain_website: str) -> Job | None:
    """Scrape a single job page for core fields."""

    page = await context.new_page()
    await page.goto(job_url, wait_until="domcontentloaded")
    title = await _extract_heading(page)
    if not title:
        logger.info("Skipping %s because no title heading was found", job_url)
        await page.close()
        return None

    location = await _text_from_labels(page, ["location", "city", "remote", "hybrid"])
    description = (await page.text_content("body")) or ""
    snippet = description[:500].strip()
    remote_flag = "remote" in description.lower() or (location or "").lower() == "remote"

    apply_link = await _first_link(page, ["apply", "submit", "continue"])

    job = Job(
        domain_id=domain_id,
        domain_title=domain_title,
        domain_website=domain_website,
        title=title,
        location=location,
        remote_flag=remote_flag,
        department=None,
        job_url=job_url,
        apply_url=apply_link or job_url,
        posted_at=None,
        discovered_at=datetime.utcnow(),
        score=0.0,
        tags=[],
        snippet=snippet,
    )
    await page.close()
    return job


async def _extract_heading(page) -> str | None:
    for selector in ["h1", "h2", "header h1"]:
        element = await page.query_selector(selector)
        if element:
            text = (await element.inner_text() or "").strip()
            if text:
                return text
    return None


async def _text_from_labels(page, labels: list[str]) -> str | None:
    body = (await page.text_content("body")) or ""
    lower = body.lower()
    for label in labels:
        marker = f"{label}:"
        if marker in lower:
            start = lower.index(marker) + len(marker)
            snippet = body[start : start + 80].split("\n")[0].strip()
            if snippet:
                return snippet
        if label in lower:
            return label.title()
    return None


async def _first_link(page, keywords: list[str]) -> str | None:
    for anchor in await page.query_selector_all("a"):
        href = await anchor.get_attribute("href")
        text = (await anchor.inner_text() or "").lower()
        if not href:
            continue
        if any(kw in text for kw in keywords):
            return urljoin(page.url, href)
    return None


async def _ats_job_links(page, base_url: str) -> Set[str]:
    """Collect job links from common ATS providers."""

    selectors = {
        "greenhouse": "a[href*='boards.greenhouse.io'], .opening a, a[data-mapped='opening']",
        "lever": "a[href*='jobs.lever.co'], a.posting-title, a[data-qa='posting-name']",
        "workable": "a[href*='apply.workable.com']",
        "ashby": "a[href*='ashbyhq.com']",
        "breezy": "a[href*='breezy.hr']",
    }

    links: Set[str] = set()
    for name, selector in selectors.items():
        anchors = await page.query_selector_all(selector)
        for anchor in anchors:
            href = await anchor.get_attribute("href")
            if href:
                links.add(urljoin(base_url, href))
        if anchors:
            logger.info("Detected %s listings at %s", name, base_url)
    return links


async def _keyword_job_links(page, base_url: str) -> Set[str]:
    """Collect job links by looking for keyword-heavy anchors in the page."""

    anchors = await page.query_selector_all("a")
    links: Set[str] = set()
    for anchor in anchors:
        href = await anchor.get_attribute("href")
        text = (await anchor.inner_text() or "").lower()
        if not href:
            continue
        href_lower = href.lower()
        if any(keyword in text for keyword in JOB_KEYWORDS) or "job" in href_lower or "career" in href_lower:
            links.add(urljoin(base_url, href))
    return links

