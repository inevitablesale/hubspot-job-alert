import hashlib
import re
import string
from typing import List, Optional
from urllib.parse import parse_qsl, urljoin, urlunparse, urlparse

from bs4 import BeautifulSoup

from backend.models import Domain, JobPosting


JOB_CLASS_KEYWORDS = ["job", "position", "opening", "opportunity", "career", "role"]


def normalize_job_title(title: str) -> str:
    lowered = title.lower()
    lowered = re.sub(r"\(remote\)|\(usa\)|\(us\)", "", lowered)
    table = str.maketrans("", "", string.punctuation)
    lowered = lowered.translate(table)
    lowered = re.sub(r"\s+", " ", lowered).strip()
    return lowered


def normalize_job_url(url: str) -> str:
    parsed = urlparse(url)
    filtered_query = "&".join(
        f"{k}={v}" for k, v in parse_qsl(parsed.query) if not k.lower().startswith("utm_")
    )
    normalized = urlunparse(
        (parsed.scheme, parsed.netloc.lower(), parsed.path.rstrip("/"), "", filtered_query, "")
    )
    return normalized


def _job_id(domain_id: str, title: str, url: str) -> str:
    norm_title = normalize_job_title(title)
    norm_url = normalize_job_url(url)
    raw = f"{domain_id}:{norm_title}:{norm_url}"
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()


def _extract_title(container) -> Optional[str]:
    for tag in ["h1", "h2", "h3", "h4", "a"]:
        el = container.find(tag)
        if el and el.get_text(strip=True):
            return el.get_text(strip=True)
    heading = container.find(attrs={"role": "heading"})
    if heading and heading.get_text(strip=True):
        return heading.get_text(strip=True)
    return None


def _extract_location(container) -> Optional[str]:
    location_candidates = container.find_all(class_=lambda c: c and "location" in c.lower())
    for loc in location_candidates:
        text = loc.get_text(" ", strip=True)
        if text:
            return text
    for label in container.find_all(string=True):
        if "location" in label.lower() and label.parent:
            sibling_text = label.parent.get_text(" ", strip=True)
            if sibling_text:
                return sibling_text.replace(label, "").strip()
    return None


def _extract_link(container, page_url: str) -> Optional[str]:
    link = container.find("a", href=True)
    if link:
        return urljoin(page_url, link.get("href"))
    return None


def _container_matches(container) -> bool:
    class_names = " ".join(container.get("class", [])).lower()
    for keyword in JOB_CLASS_KEYWORDS:
        if keyword in class_names:
            return True
    text = container.get_text(" ", strip=True).lower()
    hit_count = sum(1 for kw in JOB_CLASS_KEYWORDS if kw in text)
    return hit_count >= 2


def parse_jobs_from_html(domain: Domain, url: str, html: str, settings) -> List[JobPosting]:
    soup = BeautifulSoup(html, "html.parser")
    candidates: List[JobPosting] = []

    containers = []
    for tag in ["li", "div", "article", "tr"]:
        containers.extend(soup.find_all(tag))

    for container in containers:
        if not _container_matches(container):
            continue
        title = _extract_title(container)
        if not title:
            continue
        source_url = _extract_link(container, url) or url
        description_text = container.get_text(" ", strip=True)
        snippet = description_text[:300]
        location = _extract_location(container)
        job_id = _job_id(domain.id, title, source_url)
        candidates.append(
            JobPosting(
                id=job_id,
                domainId=domain.id,
                domainName=domain.name,
                companyWebsite=domain.website,
                sourceUrl=source_url,
                title=title,
                location=location,
                department=None,
                employmentType=None,
                remote="remote" in description_text.lower(),
                descriptionSnippet=snippet,
                isHubspotRole=False,
                matchedKeywords=[],
                scrapedAt="",
            )
        )

    if candidates:
        return candidates

    # fallback single posting
    heading = soup.find(["h1", "h2", "h3"])
    if heading and heading.get_text(strip=True):
        body_text = soup.get_text(" ", strip=True)
        if any(word in body_text.lower() for word in ["responsibilities", "requirements", "apply"]):
            title = heading.get_text(strip=True)
            job_id = _job_id(domain.id, title, url)
            candidates.append(
                JobPosting(
                    id=job_id,
                    domainId=domain.id,
                    domainName=domain.name,
                    companyWebsite=domain.website,
                    sourceUrl=url,
                    title=title,
                    location=None,
                    department=None,
                    employmentType=None,
                    remote="remote" in body_text.lower(),
                    descriptionSnippet=body_text[:300],
                    isHubspotRole=False,
                    matchedKeywords=[],
                    scrapedAt="",
                )
            )

    return candidates
