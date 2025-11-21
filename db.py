"""SQLite persistence helpers."""
from __future__ import annotations
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Optional

from config import DATABASE_FILE, DOMAINS_FILE
from models import Domain, Job, CrawlStatus


def get_connection() -> sqlite3.Connection:
    DATABASE_FILE.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DATABASE_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS domains (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            totalScore REAL,
            reviewsCount INTEGER,
            street TEXT,
            city TEXT,
            state TEXT,
            countryCode TEXT,
            website TEXT UNIQUE,
            phone TEXT,
            categoryName TEXT,
            url TEXT,
            internal_lastScannedAt TEXT,
            internal_careersUrl TEXT,
            jobsFoundLastRun INTEGER
        );
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id INTEGER,
            domain_id INTEGER NOT NULL,
            domain_title TEXT NOT NULL,
            domain_website TEXT NOT NULL,
            title TEXT NOT NULL,
            location TEXT,
            remote_flag INTEGER,
            department TEXT,
            job_url TEXT NOT NULL,
            apply_url TEXT,
            posted_at TEXT,
            discovered_at TEXT NOT NULL,
            score REAL,
            tags TEXT,
            snippet TEXT,
            FOREIGN KEY(domain_id) REFERENCES domains(id)
        );
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS crawl_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            started_at TEXT,
            finished_at TEXT,
            status TEXT,
            domains_scanned INTEGER DEFAULT 0,
            jobs_found INTEGER DEFAULT 0,
            error_count INTEGER DEFAULT 0,
            current_domain TEXT
        );
        """
    )
    conn.commit()
    conn.close()


def load_domains_from_file() -> List[Domain]:
    data = json.loads(Path(DOMAINS_FILE).read_text())
    return [Domain(**item) for item in data]


def upsert_domains(domains: Iterable[Domain]) -> None:
    conn = get_connection()
    cur = conn.cursor()
    for domain in domains:
        if not domain.website:
            continue
        cur.execute(
            """
            INSERT INTO domains (title, totalScore, reviewsCount, street, city, state, countryCode, website, phone, categoryName, url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(website) DO UPDATE SET
                title=excluded.title,
                totalScore=excluded.totalScore,
                reviewsCount=excluded.reviewsCount,
                street=excluded.street,
                city=excluded.city,
                state=excluded.state,
                countryCode=excluded.countryCode,
                phone=excluded.phone,
                categoryName=excluded.categoryName,
                url=excluded.url;
            """,
            (
                domain.title,
                domain.totalScore,
                domain.reviewsCount,
                domain.street,
                domain.city,
                domain.state,
                domain.countryCode,
                str(domain.website) if domain.website is not None else None,
                domain.phone,
                domain.categoryName,
                domain.url,
            ),
        )
    conn.commit()
    conn.close()


def list_domains() -> List[Domain]:
    conn = get_connection()
    cur = conn.cursor()
    rows = cur.execute("SELECT * FROM domains ORDER BY title").fetchall()
    conn.close()
    return [Domain(**dict(row)) for row in rows]


def create_run() -> int:
    conn = get_connection()
    cur = conn.cursor()
    started = datetime.utcnow().isoformat()
    cur.execute(
        "INSERT INTO crawl_runs (started_at, status) VALUES (?, ?)", (started, "running")
    )
    conn.commit()
    run_id = cur.lastrowid
    conn.close()
    return run_id


def update_run_status(run_id: int, **fields) -> None:
    conn = get_connection()
    cur = conn.cursor()
    sets = ", ".join(f"{k} = ?" for k in fields.keys())
    values = list(fields.values())
    values.append(run_id)
    cur.execute(f"UPDATE crawl_runs SET {sets} WHERE id = ?", values)
    conn.commit()
    conn.close()


def record_job(job: Job, run_id: Optional[int] = None) -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO jobs (run_id, domain_id, domain_title, domain_website, title, location, remote_flag, department, job_url, apply_url, posted_at, discovered_at, score, tags, snippet)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            run_id,
            job.domain_id,
            job.domain_title,
            job.domain_website,
            job.title,
            job.location,
            1 if job.remote_flag else 0,
            job.department,
            job.job_url,
            job.apply_url,
            job.posted_at.isoformat() if job.posted_at else None,
            job.discovered_at.isoformat(),
            job.score,
            json.dumps(job.tags),
            job.snippet,
        ),
    )
    conn.commit()
    conn.close()


def fetch_jobs(run_id: Optional[int] = None, min_score: Optional[float] = None, tag: Optional[str] = None) -> List[Job]:
    conn = get_connection()
    cur = conn.cursor()
    if run_id is None:
        latest = cur.execute(
            "SELECT id FROM crawl_runs WHERE status = 'completed' ORDER BY started_at DESC LIMIT 1"
        ).fetchone()
        if latest:
            run_id = latest["id"]
    query = "SELECT * FROM jobs"
    clauses = []
    params: List[object] = []
    if run_id is not None:
        clauses.append("run_id = ?")
        params.append(run_id)
    if min_score is not None:
        clauses.append("score >= ?")
        params.append(min_score)
    if tag:
        clauses.append("tags LIKE ?")
        params.append(f"%{tag}%")
    if clauses:
        query += " WHERE " + " AND ".join(clauses)
    query += " ORDER BY discovered_at DESC"
    rows = cur.execute(query, params).fetchall()
    conn.close()
    return [Job(**_row_to_job(row)) for row in rows]


def _row_to_job(row: sqlite3.Row) -> dict:
    data = dict(row)
    data["remote_flag"] = bool(data.get("remote_flag")) if data.get("remote_flag") is not None else None
    data["tags"] = json.loads(data.get("tags") or "[]")
    data["posted_at"] = datetime.fromisoformat(data["posted_at"]) if data.get("posted_at") else None
    data["discovered_at"] = datetime.fromisoformat(data["discovered_at"])
    return data


def get_status(run_id: Optional[int] = None) -> CrawlStatus:
    conn = get_connection()
    cur = conn.cursor()
    if run_id:
        row = cur.execute("SELECT * FROM crawl_runs WHERE id = ?", (run_id,)).fetchone()
    else:
        row = cur.execute("SELECT * FROM crawl_runs ORDER BY started_at DESC LIMIT 1").fetchone()
    if not row:
        return CrawlStatus(status="idle", runId=None)
    status_row = dict(row)
    result = CrawlStatus(
        runId=status_row["id"],
        status=status_row["status"],
        startedAt=datetime.fromisoformat(status_row["started_at"]) if status_row.get("started_at") else None,
        finishedAt=datetime.fromisoformat(status_row["finished_at"]) if status_row.get("finished_at") else None,
        domainsTotal=len(list_domains()),
        domainsCompleted=status_row.get("domains_scanned") or 0,
        jobsFound=status_row.get("jobs_found") or 0,
        currentDomain=status_row.get("current_domain"),
        errorCount=status_row.get("error_count") or 0,
    )
    conn.close()
    return result

