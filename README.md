# HubSpot Job Alert

This project provides a small FastAPI + React service that crawls a curated list of HubSpot-related agencies and companies, discovers their careers pages, extracts job listings with Playwright, classifies them, and surfaces the results in a dashboard.

## Getting started

### Backend
1. Create a virtualenv and install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Install Playwright browsers (once):
   ```bash
   python -m playwright install chromium --with-deps
   ```
3. Run the API locally:
   ```bash
   uvicorn server:app --reload
   ```

The API exposes endpoints under `/api/*` and serves the built frontend at `/` when compiled.

### Frontend
```
cd frontend
npm install
npm run build
```
The Vite build outputs to `frontend/dist`, which is served by FastAPI (and also copied to `static/` during Render deploys via `postinstall.sh`).

### Deployment
Render uses the provided commands:
- **Build:** `./postinstall.sh`
- **Start:** `uvicorn server:app --host 0.0.0.0 --port $PORT`

`server.py` includes all API routes and static serving configuration required for Render.

### Configuration
- `DOMAINS_FILE` points to the source of truth for the domains to crawl. It must be provided via the deployment secret at `/etc/secrets/DOMAINS_FILE` (or by setting the `DOMAINS_FILE` environment variable). Records are upserted into SQLite on startup.
- SQLite database lives at `/data/jobs.db` (override with `DATA_DIR`) so runs persist across restarts.
- Logs are written to stdout and `data/logs.txt` (rotating at 5MB).

## Frontend features
- Trigger scans and poll status.
- View domains, progress, recent logs, and discovered jobs with filters for search, remote-only, and minimum score.

## Crawler overview
- Playwright launches headless Chromium for robust page rendering.
- Careers page discovery uses anchor heuristics and common paths.
- Job extraction gathers likely listing links, fetches detail pages, and captures titles/snippets.
- A lightweight classifier assigns tags and a relevance score based on keywords and domain context.

## How domain crawling works
1. **Load the canonical list** – On startup the API reads the JSON list from `DOMAINS_FILE` (expected at `/etc/secrets/DOMAINS_FILE`) and upserts each company into the `domains` table so every crawl is anchored to that source of truth. 
2. **Spin up a run** – When `/api/run` is invoked, a crawl run is created in SQLite and a background coroutine iterates through the selected domains. Each domain record provides the `website` that seeds navigation. 
3. **Locate a careers page** – For every domain the crawler opens the homepage in Playwright, scans all anchors for career-related keywords, and also probes common paths like `/careers` or `/jobs`. The highest-confidence URL is returned as the careers page candidate. 
4. **Discover job links** – The crawler loads the careers page and collects candidate postings in two passes: (a) ATS-aware selectors for Greenhouse, Lever, Workable, Ashby, and Breezy; and (b) keyword-heavy anchors or URLs that mention jobs or careers. 
5. **Scrape details** – Each candidate job URL is opened, headings are captured as titles, location and remote hints are parsed from page text, and an apply link is pulled from action-oriented anchors. A snippet from the body is included for quick preview.
6. **Classify and store** – The scraped job is scored and tagged, then persisted with the run ID so `/api/status`, `/api/results`, and `/api/logs` reflect progress domain by domain.

