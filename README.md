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
- `DOMAINS_FILE` points to the source of truth for the domains to crawl (by default `data/domains.json`; in Render it is provided at `/etc/secrets/DOMAINS_FILE`). Records are upserted into SQLite on startup.
- SQLite database lives at `data/jobs.db` and is created automatically.
- Logs are written to stdout and `data/logs.txt` (rotating at 5MB).

## Frontend features
- Trigger scans and poll status.
- View domains, progress, recent logs, and discovered jobs with filters for search, remote-only, and minimum score.

## Crawler overview
- Playwright launches headless Chromium for robust page rendering.
- Careers page discovery uses anchor heuristics and common paths.
- Job extraction gathers likely listing links, fetches detail pages, and captures titles/snippets.
- A lightweight classifier assigns tags and a relevance score based on keywords and domain context.

