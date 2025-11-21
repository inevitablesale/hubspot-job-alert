"""
Quick ad-hoc script to crawl a few domains and print discovered jobs.

Usage (from repository root):
    export DOMAINS_FILE_PATH=./domains.json
    python backend/test_crawler.py
"""

import os

from backend.config import get_settings
from backend.crawler.jobs_crawler import crawl_jobs_for_domain
from backend.storage.memory_store import DOMAINS, load_domains_from_file


if __name__ == "__main__":
    settings = get_settings()
    load_domains_from_file(settings.DOMAINS_FILE_PATH)
    subset = list(DOMAINS.values())[:3]
    print(f"Testing {len(subset)} domains from {os.path.abspath(settings.DOMAINS_FILE_PATH)}")
    for domain in subset:
        jobs = crawl_jobs_for_domain(domain, settings)
        hubspot_jobs = [job for job in jobs if job.isHubspotRole]
        print(
            f"Domain: {domain.name} ({domain.website}) -> {len(jobs)} jobs, {len(hubspot_jobs)} HubSpot-related"
        )
        for job in hubspot_jobs:
            print(f"  - {job.title} @ {job.sourceUrl} | keywords: {', '.join(job.matchedKeywords)}")
