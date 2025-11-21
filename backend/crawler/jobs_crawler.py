from typing import Dict, List, Optional, Set, Tuple

import requests
from bs4 import BeautifulSoup

from backend.config import Settings
from backend.crawler.careers_discovery import discover_career_urls
from backend.crawler.html_parsing import normalize_job_url, parse_jobs_from_html
from backend.models import Domain, JobPosting
from backend.storage import memory_store
from backend.utils import logger


HEADERS = {"User-Agent": "hubspot-job-alert/1.0"}


def _match_hubspot_role(job: JobPosting, settings: Settings) -> Tuple[bool, List[str]]:
    text = f"{job.title} {job.descriptionSnippet}".lower()
    matched = [kw for kw in settings.HUBSPOT_ROLE_KEYWORDS if kw in text]
    exclude_hit = any(kw in text for kw in settings.HUBSPOT_EXCLUDE_KEYWORDS)
    if not matched:
        return False, []
    if exclude_hit and not matched:
        return False, []
    return True, matched


def _respect_robots(base_url: str) -> List[str]:
    try:
        response = requests.get(f"{base_url}/robots.txt", headers=HEADERS, timeout=5)
        if response.status_code >= 400:
            return []
    except Exception:
        return []
    disallowed: List[str] = []
    for line in response.text.splitlines():
        if line.lower().startswith("disallow:"):
            path = line.split(":", 1)[1].strip()
            if path:
                disallowed.append(path)
    for blocked in disallowed:
        if any(signal in blocked for signal in ["careers", "jobs"]):
            logger.warning("robots.txt blocks careers paths", {"domain": base_url, "path": blocked})
    return disallowed


def _is_excluded_path(path: str, settings: Settings, robots_disallow: List[str]) -> bool:
    for prefix in settings.CRAWLER_EXCLUDE_PATH_PREFIXES:
        if path.startswith(prefix):
            return True
    for path_rule in robots_disallow:
        if path_rule.strip() == "/":
            continue
        if any(signal in path_rule for signal in ["careers", "job"]):
            # log only, do not exclude
            continue
        if path.startswith(path_rule.rstrip("*")):
            return True
    return False


def _discover_pagination_links(soup: BeautifulSoup, page_url: str, root_path: str) -> List[str]:
    links: List[str] = []
    for anchor in soup.find_all("a", href=True):
        text = anchor.get_text(strip=True).lower()
        href = anchor.get("href")
        if not href:
            continue
        candidate = requests.compat.urljoin(page_url, href)
        parsed = requests.compat.urlparse(candidate)
        if parsed.fragment:
            candidate = requests.compat.urlunparse(
                (parsed.scheme, parsed.netloc, parsed.path, parsed.params, parsed.query, "")
            )
        if len(candidate) > 200:
            continue
        if not parsed.path.startswith(root_path):
            continue
        if any(token in text for token in ["next", "older", "more"]):
            links.append(candidate)
            continue
        if "page" in parsed.query or "/page/" in parsed.path:
            links.append(candidate)
    return links


def crawl_jobs_for_domain(domain: Domain, settings: Settings) -> List[JobPosting]:
    logger.info("Discovering career URLs", {"domain": domain.website, "domainId": domain.id})
    career_urls = discover_career_urls(domain.website)
    if not career_urls:
        logger.warning("No careers URLs discovered", {"domain": domain.website, "domainId": domain.id})
        return []

    robots_disallow = _respect_robots(domain.website)
    seen_ids: Set[str] = set()
    jobs: List[JobPosting] = []
    for careers_url in career_urls:
        page_queue = [careers_url]
        seen_pages: Set[str] = set()
        root_path = requests.compat.urlparse(careers_url).path or "/"
        while page_queue and len(seen_pages) < settings.CRAWLER_MAX_PAGINATION_PAGES:
            page_url = page_queue.pop(0)
            parsed = requests.compat.urlparse(page_url)
            if (
                len(page_url) > settings.CRAWLER_URL_MAX_LENGTH
                or _is_excluded_path(parsed.path, settings, robots_disallow)
            ):
                continue
            if page_url in seen_pages:
                continue
            seen_pages.add(page_url)
            try:
                response = requests.get(page_url, headers=HEADERS, timeout=10)
                response.raise_for_status()
                memory_store.mark_domain_fetch_ok(domain.id)
            except Exception as exc:
                logger.warning(
                    "Error fetching careers page",
                    {"url": page_url, "error": str(exc), "domainId": domain.id},
                )
                continue

            soup = BeautifulSoup(response.text, "html.parser")
            parsed_jobs = parse_jobs_from_html(domain, page_url, response.text, settings)
            for job in parsed_jobs:
                is_hubspot, matched = _match_hubspot_role(job, settings)
                job.isHubspotRole = is_hubspot
                job.matchedKeywords = matched
                job.scrapedAt = memory_store.now_iso()
                normalized_source = normalize_job_url(job.sourceUrl)
                dedupe_key = f"{job.domainId}:{normalized_source}:{job.id}"
                if dedupe_key in seen_ids:
                    continue
                seen_ids.add(dedupe_key)
                jobs.append(job)

            if len(seen_pages) < settings.CRAWLER_MAX_PAGINATION_PAGES:
                pagination_links = _discover_pagination_links(soup, page_url, root_path)
                for link in pagination_links:
                    if link not in seen_pages and link not in page_queue:
                        page_queue.append(link)

    return jobs


def run_full_crawl(
    domains: List[Domain],
    settings: Settings,
    status_store=memory_store,
    job_store=memory_store,
):
    status_store.STATUS.running = True
    status_store.STATUS.totalDomains = len(domains)
    status_store.STATUS.lastRunStartedAt = memory_store.now_iso()
    status_store.STATUS.completedDomains = 0
    status_store.STATUS.jobsFoundThisRun = 0
    status_store.STATUS.errorCount = 0

    logger.info("Starting crawl", {"total_domains": len(domains)})

    for idx, domain in enumerate(domains, start=1):
        status_store.STATUS.currentDomainId = domain.id
        status_store.STATUS.currentDomainName = domain.name
        logger.info(
            "Crawling domain",
            {"domain": domain.website, "domainId": domain.id, "index": idx, "total": len(domains)},
        )
        try:
            jobs = crawl_jobs_for_domain(domain, settings)
            status_store.STATUS.jobsFoundThisRun += len(jobs)
            job_store.add_jobs(jobs)
            if jobs:
                logger.info(
                    "Jobs found",
                    {"domain": domain.website, "domainId": domain.id, "count": len(jobs)},
                )
        except Exception as exc:
            status_store.STATUS.errorCount += 1
            logger.error(
                "Domain crawl failed", {"domain": domain.website, "domainId": domain.id, "error": str(exc)}
            )
        status_store.STATUS.completedDomains += 1

    status_store.STATUS.running = False
    status_store.STATUS.lastRunCompletedAt = memory_store.now_iso()
    status_store.STATUS.currentDomainId = None
    status_store.STATUS.currentDomainName = None
    logger.info("Crawl completed", {"completed": status_store.STATUS.completedDomains})
