from typing import List, Tuple
from urllib.parse import urljoin, urlparse, urlunparse

import requests
from bs4 import BeautifulSoup

CAREER_SIGNALS = [
    "career",
    "careers",
    "jobs",
    "join-us",
    "join us",
    "work-with-us",
    "work with us",
    "team",
    "open-positions",
    "open positions",
]


def _normalize_base(url: str) -> str:
    trimmed = (url or "").strip()
    if not trimmed:
        return ""
    if not trimmed.startswith("http://") and not trimmed.startswith("https://"):
        trimmed = f"https://{trimmed}"
    parsed = urlparse(trimmed)
    normalized = urlunparse(("https", parsed.netloc.lower(), parsed.path.rstrip("/"), "", "", ""))
    return normalized


def _same_domain(url: str, base_netloc: str) -> bool:
    netloc = urlparse(url).netloc.lower()
    return netloc == base_netloc or netloc.replace("www.", "") == base_netloc.replace("www.", "")


def _score_link(url: str, text: str) -> int:
    score = 0
    lower_url = url.lower()
    lower_text = (text or "").lower()
    for signal in CAREER_SIGNALS:
        if signal in lower_url:
            score += 3
        if signal in lower_text:
            score += 2
    return score


def discover_career_urls(website: str, max_pages: int = 15) -> List[str]:
    base_url = _normalize_base(website)
    if not base_url:
        return []

    headers = {"User-Agent": "hubspot-job-alert/1.0"}
    try:
        response = requests.get(base_url, headers=headers, timeout=10)
        response.raise_for_status()
    except Exception:
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    candidates: List[Tuple[int, str]] = []
    base_netloc = urlparse(base_url).netloc

    for anchor in soup.find_all("a"):
        href = anchor.get("href")
        text = anchor.get_text(strip=True)
        if not href:
            continue
        if href.startswith("javascript"):
            # modal triggers: treat as on-page content
            if anchor.has_attr("data-target") or text.lower() in CAREER_SIGNALS:
                candidates.append((2, base_url))
            continue
        if href.startswith("#"):
            # treat as on-page section
            if _score_link(base_url, text) > 0:
                candidates.append((2, base_url))
            continue
        candidate_url = urljoin(base_url + "/", href)
        parsed = urlparse(candidate_url)
        if not parsed.scheme.startswith("http"):
            continue
        if parsed.fragment:
            candidate_url = urlunparse(
                (parsed.scheme, parsed.netloc, parsed.path, parsed.params, parsed.query, "")
            )
        if not parsed.path:
            continue
        if not _same_domain(candidate_url, base_netloc):
            continue
        score = _score_link(candidate_url, text)
        if score <= 0:
            continue
        candidates.append((score, candidate_url.rstrip("/")))

    sorted_candidates: List[str] = []
    seen = set()
    for score, url in sorted(candidates, key=lambda item: item[0], reverse=True):
        if url in seen:
            continue
        seen.add(url)
        sorted_candidates.append(url)
        if len(sorted_candidates) >= max_pages:
            break

    return sorted_candidates
