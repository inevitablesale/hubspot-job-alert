from typing import List, Optional

from pydantic import BaseModel


class Domain(BaseModel):
    id: str
    name: str
    website: str
    city: Optional[str]
    state: Optional[str]
    countryCode: Optional[str]
    categoryName: Optional[str]
    sourceUrl: str
    totalScore: Optional[float]
    reviewsCount: Optional[int]
    lastOkFetchAt: Optional[str] = None


class JobPosting(BaseModel):
    id: str
    domainId: str
    domainName: str
    companyWebsite: str
    sourceUrl: str
    title: str
    location: Optional[str]
    department: Optional[str]
    employmentType: Optional[str]
    remote: Optional[bool]
    descriptionSnippet: str
    isHubspotRole: bool
    matchedKeywords: List[str]
    scrapedAt: str


class CrawlStatus(BaseModel):
    running: bool = False
    lastRunStartedAt: Optional[str]
    lastRunCompletedAt: Optional[str]
    currentDomainId: Optional[str]
    currentDomainName: Optional[str]
    totalDomains: int = 0
    completedDomains: int = 0
    jobsFoundThisRun: int = 0
    errorCount: int = 0


class LogEntry(BaseModel):
    timestamp: str
    level: str
    message: str
    context: dict
