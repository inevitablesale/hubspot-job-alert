"""Job listing extraction."""
from __future__ import annotations
import logging
from datetime import datetime
from typing import List
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
    jobs: List[Job] = []
    page = await context.new_page()
    await page.goto(careers_url, wait_until="domcontentloaded")
    anchors = await page.query_selector_all("a")
    candidates: list[str] = []
    for anchor in anchors:
        href = await anchor.get_attribute("href")
        text = (await anchor.inner_text() or "").lower()
        if not href:
            continue
        if any(keyword in text for keyword in JOB_KEYWORDS):
            full_url = urljoin(careers_url, href)
            candidates.append(full_url)
    seen = []
    for url in candidates:
        if url in seen:
            continue
        seen.append(url)
        try:
            job = await scrape_job_detail(context, url, domain_id, domain_title, domain_website)
            if job:
                jobs.append(job)
        except Exception as exc:  # noqa: BLE001
            logger.error("Failed to scrape %s: %s", url, exc)
    await page.close()
    return jobs


async def scrape_job_detail(context: BrowserContext, job_url: str, domain_id: int, domain_title: str, domain_website: str) -> Job | None:
    page = await context.new_page()
    await page.goto(job_url, wait_until="domcontentloaded")
    title = await _extract_heading(page)
    if not title:
        await page.close()
        return None
    location = await _text_from_labels(page, ["location", "city", "remote"])
    description = (await page.text_content("body")) or ""
    snippet = description[:400].strip()
    remote_flag = "remote" in description.lower()
    job = Job(
        domain_id=domain_id,
        domain_title=domain_title,
        domain_website=domain_website,
        title=title,
        location=location,
        remote_flag=remote_flag,
        department=None,
        job_url=job_url,
        apply_url=job_url,
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
        if label in lower:
            return label.title()
    return None

