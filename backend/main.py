import json
from typing import List, Optional

import uvicorn
from fastapi import BackgroundTasks, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from backend.config import get_settings
from backend.crawler.jobs_crawler import crawl_jobs_for_domain, run_full_crawl
from backend.crawler.careers_discovery import discover_career_urls
from backend.models import CrawlStatus, Domain, JobPosting, LogEntry
from backend.storage import file_store, memory_store
from backend.storage.memory_store import load_domains_from_file
from backend.utils import logger

app = FastAPI(title="HubSpot Job Alert")
settings = get_settings()

origins = ["http://localhost:5173", "*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _load_state():
    try:
        domains = load_domains_from_file(settings.DOMAINS_FILE_PATH)
    except FileNotFoundError:
        logger.error(
            "Domains file missing; set DOMAINS_FILE_PATH or place domains.json at repo root",
            {"path": settings.DOMAINS_FILE_PATH},
        )
        domains = {}
    except Exception as exc:
        logger.error(
            "Failed loading domains file",
            {"path": settings.DOMAINS_FILE_PATH, "error": str(exc)},
        )
        domains = {}

    saved_jobs = file_store.load_jobs_from_file()
    if saved_jobs:
        memory_store.JOBS.update(saved_jobs)
    memory_store.STATUS.totalDomains = len(domains)
    logger.info(
        "Startup complete",
        {"domains": len(domains), "jobs_loaded": len(saved_jobs), "domains_path": settings.DOMAINS_FILE_PATH},
    )


@app.on_event("startup")
async def startup_event():
    _load_state()


class RunRequest(Domain):
    class Config:
        orm_mode = True


@app.get("/domains", response_model=List[Domain])
def list_domains(q: Optional[str] = Query(None)):
    domains = list(memory_store.DOMAINS.values())
    if q:
        query = q.lower()
        domains = [d for d in domains if query in d.name.lower() or query in d.website.lower()]
    return domains


@app.get("/domains/{domain_id}/careers", response_model=List[str])
def preview_careers(domain_id: str):
    domain = memory_store.DOMAINS.get(domain_id)
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")
    urls = discover_career_urls(domain.website, max_pages=5)
    return urls


@app.post("/run")
def run_crawl(background_tasks: BackgroundTasks, domainId: Optional[str] = None):
    if memory_store.STATUS.running:
        raise HTTPException(status_code=409, detail="Crawl in progress")

    domains_to_crawl: List[Domain]
    if domainId:
        domain = memory_store.DOMAINS.get(domainId)
        if not domain:
            raise HTTPException(status_code=404, detail="Domain not found")
        domains_to_crawl = [domain]
    else:
        domains_to_crawl = list(memory_store.DOMAINS.values())

    def task():
        memory_store.reset_status(len(domains_to_crawl))
        run_full_crawl(domains_to_crawl, settings)
        file_store.save_jobs_to_file(list(memory_store.JOBS.values()))

    background_tasks.add_task(task)
    return {"started": True, "scope": "single" if domainId else "full", "domainId": domainId or None}


@app.get("/status", response_model=CrawlStatus)
def get_status():
    return memory_store.STATUS


@app.get("/results", response_model=List[JobPosting])
def get_results(limit: int = 200, hubspotOnly: bool = True):
    jobs = memory_store.get_jobs(limit=limit)
    if hubspotOnly:
        jobs = [job for job in jobs if job.isHubspotRole]
    return jobs


@app.get("/logs", response_model=List[LogEntry])
def get_logs():
    return memory_store.get_logs()


if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="0.0.0.0", port=settings.PORT, reload=True)
