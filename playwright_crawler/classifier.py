"""Rule-based job classification and scoring."""
from __future__ import annotations
from typing import List

from models import Job

HUBSPOT_TERMS = ["hubspot", "crm", "marketing ops", "revops"]
TECH_TERMS = ["developer", "engineer", "software", "data", "ai"]
COMMERCIAL_TERMS = ["sales", "account", "manager"]
NON_RELEVANT = ["facility", "janitor", "reception"]


def classify_job(job: Job, category_hint: str | None = None) -> Job:
    description = (job.snippet or "" + job.title).lower()
    tags: List[str] = []
    score = 0.0

    if any(term in description for term in HUBSPOT_TERMS):
        tags.append("hubspot")
        score += 2
    if any(term in description for term in TECH_TERMS):
        tags.append("developer")
        score += 1
    if any(term in description for term in COMMERCIAL_TERMS):
        tags.append("sales")
        score += 0.5
    if job.remote_flag:
        score += 1
        tags.append("remote")
    if category_hint and "marketing" in category_hint.lower():
        score += 1
    if any(term in description for term in NON_RELEVANT):
        score -= 1

    score = max(0.0, min(10.0, score))
    job.score = score
    job.tags = tags
    return job

