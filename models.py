"""Pydantic models used across the API."""
from __future__ import annotations
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, HttpUrl


class Domain(BaseModel):
    id: Optional[int] = None
    title: str
    totalScore: Optional[float] = None
    reviewsCount: Optional[int] = None
    street: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    countryCode: Optional[str] = None
    website: Optional[HttpUrl] = None
    phone: Optional[str] = None
    categoryName: Optional[str] = None
    url: Optional[str] = None
    internal_lastScannedAt: Optional[datetime] = None
    internal_careersUrl: Optional[str] = None
    jobsFoundLastRun: Optional[int] = None


class Job(BaseModel):
    id: Optional[int] = None
    run_id: Optional[int] = None
    domain_id: int
    domain_title: str
    domain_website: str
    title: str
    location: Optional[str] = None
    remote_flag: Optional[bool] = None
    department: Optional[str] = None
    job_url: str
    apply_url: Optional[str] = None
    posted_at: Optional[datetime] = None
    discovered_at: datetime
    score: float
    tags: List[str] = Field(default_factory=list)
    snippet: Optional[str] = None


class CrawlRequest(BaseModel):
    domains: Optional[List[str]] = None


class CrawlStatus(BaseModel):
    runId: Optional[int]
    status: str
    startedAt: Optional[datetime] = None
    finishedAt: Optional[datetime] = None
    domainsTotal: int = 0
    domainsCompleted: int = 0
    jobsFound: int = 0
    currentDomain: Optional[str] = None
    lastLogMessage: Optional[str] = None
    errorCount: int = 0


class RunResponse(BaseModel):
    run_id: int
    started_at: datetime

