"""FastAPI entrypoint for the job crawler."""
from __future__ import annotations
import asyncio
import logging
from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from config import DOMAINS_FILE, STATIC_DIR, FRONTEND_DIST
from db import (
    create_run,
    fetch_jobs,
    get_status,
    init_db,
    list_domains,
    load_domains_from_file,
    record_job,
    upsert_domains,
    update_run_status,
)
from logging_utils import configure_logging, tail_logs
from models import CrawlRequest, CrawlStatus, Domain, Job, RunResponse
from playwright_crawler.browser import browser_context
from playwright_crawler.careers import discover_careers_page
from playwright_crawler.classifier import classify_job
from playwright_crawler.jobs import extract_jobs

configure_logging()
logger = logging.getLogger(__name__)

app = FastAPI(title="HubSpot Job Alert")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

current_crawl_task: Optional[asyncio.Task] = None
# Central queue to keep crawl work alive even after the HTTP request returns.
run_queue: asyncio.Queue[tuple[int, Optional[List[str]]]] = asyncio.Queue()
worker_task: Optional[asyncio.Task] = None


@app.on_event("startup")
def startup_event() -> None:
    logger.info("Booting application")
    init_db()
    domains = load_domains_from_file()
    upsert_domains(domains)
    logger.info("Loaded %d domains from %s", len(domains), DOMAINS_FILE)
    if FRONTEND_DIST.exists():
        STATIC_DIR.mkdir(exist_ok=True)
    # Launch a persistent worker so Render cannot garbage-collect background tasks.
    global worker_task
    loop = asyncio.get_event_loop()
    if worker_task is None or worker_task.done():
        worker_task = loop.create_task(crawl_worker())


async def crawl_domains(run_id: int, domain_filters: Optional[List[str]]) -> None:
    status = get_status(run_id)
    domains = list_domains()
    if domain_filters:
        domain_filters_lower = {d.lower() for d in domain_filters}
        domains = [d for d in domains if (d.website or "").lower() in domain_filters_lower or str(d.id) in domain_filters_lower]
    update_run_status(run_id, domains_scanned=0, jobs_found=0, status="running")
    total_found = 0
    errors = 0

    try:
        async with browser_context() as context:
            for index, domain in enumerate(domains, start=1):
                if not domain.website:
                    logger.warning("Skipping domain %s because no website provided", domain.title)
                    errors += 1
                    continue
                logger.info("Scanning %s", domain.website)
                update_run_status(run_id, current_domain=domain.website, domains_scanned=index - 1)
                try:
                    careers_url = await discover_careers_page(context, domain.website)
                    if not careers_url:
                        logger.info("No careers page found for %s", domain.title)
                        continue
                    jobs = await extract_jobs(context, careers_url, domain.id or 0, domain.title, domain.website)
                    logger.info("Found %d potential jobs for %s", len(jobs), domain.title)
                    for job in jobs:
                        scored = classify_job(job, domain.categoryName)
                        record_job(scored, run_id=run_id)
                    total_found += len(jobs)
                except Exception as exc:  # noqa: BLE001
                    errors += 1
                    logger.exception("Error scanning %s: %s", domain.website, exc)
                update_run_status(run_id, domains_scanned=index, jobs_found=total_found)
                await asyncio.sleep(0.5)
    finally:
        update_run_status(
            run_id,
            status="completed",
            finished_at=datetime.utcnow().isoformat(),
            jobs_found=total_found,
            error_count=errors,
            current_domain=None,
        )


async def crawl_worker() -> None:
    """Persistent worker that processes crawl requests sequentially.

    Render can drop background tasks spawned per-request. This worker lives for
    the lifetime of the process and pulls jobs from a queue so crawls continue
    after the HTTP response returns.
    """
    logger.info("Crawl worker booted and awaiting tasks")
    while True:
        run_id, domain_filters = await run_queue.get()
        logger.info("Starting queued crawl run %s", run_id)
        try:
            global current_crawl_task
            current_crawl_task = asyncio.current_task()
            await crawl_domains(run_id, domain_filters)
        except Exception as exc:  # noqa: BLE001
            logger.exception("Crawl run %s failed: %s", run_id, exc)
            update_run_status(
                run_id,
                status="failed",
                finished_at=datetime.utcnow().isoformat(),
                current_domain=None,
            )
        finally:
            run_queue.task_done()
            current_crawl_task = None


@app.post("/api/run", response_model=RunResponse)
async def run_crawl(request: CrawlRequest) -> RunResponse:
    global current_crawl_task
    # If a crawl is already running, refuse to enqueue another to avoid overlap.
    if current_crawl_task and not current_crawl_task.done():
        raise HTTPException(status_code=400, detail="Crawl already running")

    run_id = create_run()
    logger.info("Run %s enqueued with %d domain filters", run_id, len(request.domains or []))
    await run_queue.put((run_id, request.domains))

    # Track currently executing task handle for status checks; when the queue
    # worker picks up the item, it will replace this handle.
    current_crawl_task = worker_task
    status = get_status(run_id)
    return RunResponse(run_id=run_id, started_at=status.startedAt or datetime.utcnow())


@app.get("/api/status", response_model=CrawlStatus)
async def status_endpoint(run_id: Optional[int] = None) -> CrawlStatus:
    return get_status(run_id)


@app.get("/api/results", response_model=List[Job])
async def results_endpoint(run_id: Optional[int] = None, min_score: Optional[float] = None, tag: Optional[str] = None) -> List[Job]:
    return fetch_jobs(run_id=run_id, min_score=min_score, tag=tag)


@app.get("/api/domains", response_model=List[Domain])
async def domains_endpoint() -> List[Domain]:
    return list_domains()


@app.get("/api/logs")
async def logs_endpoint(lines: int = 100) -> JSONResponse:
    return JSONResponse({"logs": tail_logs(lines)})


@app.get("/")
async def serve_frontend_root():
    index_path = FRONTEND_DIST / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return {"message": "Frontend not built yet"}


if FRONTEND_DIST.exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIST / "assets"), name="assets")

