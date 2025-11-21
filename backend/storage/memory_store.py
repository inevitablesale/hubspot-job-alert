import hashlib
import json
import re
from datetime import datetime
from typing import Dict, List, Tuple
from urllib.parse import parse_qsl, urlparse, urlunparse

import requests

from backend.models import CrawlStatus, Domain, JobPosting, LogEntry

DOMAINS: Dict[str, Domain] = {}
JOBS: Dict[str, JobPosting] = {}
STATUS: CrawlStatus = CrawlStatus(running=False, totalDomains=0)
LOGS: List[LogEntry] = []


INVALID_HOSTS = ["facebook.com", "linkedin.com", "yelp.com", "godaddy.com"]


def normalize_website(url: str) -> str:
    cleaned = (url or "").strip()
    if not cleaned:
        return ""
    if not cleaned.startswith("http://") and not cleaned.startswith("https://"):
        cleaned = f"https://{cleaned}"
    parsed = urlparse(cleaned)
    scheme = "https"
    netloc = parsed.netloc or parsed.path
    netloc = netloc.lower()
    if netloc and not netloc.startswith("www."):
        netloc = f"www.{netloc}"
    if not netloc:
        return ""
    # drop tracking query params
    filtered_query = "&".join(
        f"{k}={v}" for k, v in parse_qsl(parsed.query) if not k.lower().startswith("utm_")
    )
    normalized = urlunparse((scheme, netloc, parsed.path.rstrip("/"), "", filtered_query, ""))
    return normalized


def _is_invalid_host(hostname: str) -> bool:
    base = hostname.replace("www.", "")
    return any(base.endswith(bad) or bad in base for bad in INVALID_HOSTS)


def _website_is_reachable(url: str) -> bool:
    if not url:
        return False
    try:
        response = requests.head(url, allow_redirects=True, timeout=5)
        if response.status_code == 405:
            response = requests.get(url, allow_redirects=True, timeout=5)
        final_host = urlparse(response.url).netloc
        if _is_invalid_host(final_host):
            return False
        if response.status_code >= 400:
            return False
        return True
    except Exception:
        return False


def _domain_id(website: str, title: str) -> str:
    base = f"{website.lower()}::{title.strip().lower()}"
    digest = hashlib.sha1(base.encode("utf-8")).hexdigest()
    slug = re.sub(r"[^a-z0-9]+", "-", title.strip().lower()).strip("-")
    return f"{slug}-{digest[:8]}"


def load_domains_from_file(path: str) -> Dict[str, Domain]:
    global DOMAINS, STATUS
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    dedup: Dict[Tuple[str, str], Domain] = {}
    for entry in raw:
        website_raw = entry.get("website") or ""
        name = entry.get("title") or entry.get("name") or website_raw
        normalized_website = normalize_website(website_raw)
        if not normalized_website:
            continue
        if _is_invalid_host(urlparse(normalized_website).netloc):
            continue
        if not _website_is_reachable(normalized_website):
            continue
        key = (normalized_website, name.strip().lower())
        if key in dedup:
            continue
        domain_id = _domain_id(normalized_website, name)
        dedup[key] = Domain(
            id=domain_id,
            name=name,
            website=normalized_website,
            city=entry.get("city"),
            state=entry.get("state"),
            countryCode=entry.get("countryCode"),
            categoryName=entry.get("categoryName"),
            sourceUrl=entry.get("url") or entry.get("sourceUrl") or normalized_website,
            totalScore=entry.get("totalScore"),
            reviewsCount=entry.get("reviewsCount"),
            lastOkFetchAt=None,
        )
    DOMAINS = dedup
    STATUS = CrawlStatus(
        running=False,
        totalDomains=len(DOMAINS),
        completedDomains=0,
        jobsFoundThisRun=0,
        errorCount=0,
    )
    return DOMAINS


def add_jobs(jobs: List[JobPosting]):
    for job in jobs:
        JOBS[job.id] = job


def get_jobs(limit: int = 200) -> List[JobPosting]:
    sorted_jobs = sorted(JOBS.values(), key=lambda j: j.scrapedAt, reverse=True)
    return sorted_jobs[:limit]


def append_log(entry: LogEntry):
    LOGS.append(entry)
    if len(LOGS) > 200:
        LOGS.pop(0)


def get_logs() -> List[LogEntry]:
    return list(LOGS)


def mark_domain_fetch_ok(domain_id: str):
    domain = DOMAINS.get(domain_id)
    if not domain:
        return
    domain.lastOkFetchAt = now_iso()


def reset_status(total_domains: int):
    global STATUS
    STATUS = CrawlStatus(
        running=False,
        totalDomains=total_domains,
        completedDomains=0,
        jobsFoundThisRun=0,
        errorCount=0,
    )


def now_iso() -> str:
    return datetime.utcnow().isoformat() + "Z"
