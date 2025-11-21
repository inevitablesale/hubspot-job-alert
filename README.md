# HubSpot Job Alert

Monitor partner domains for HubSpot-related job postings. The system discovers real careers pages, crawls job listings, filters for HubSpot roles, and exposes a FastAPI backend with a React dashboard frontend.

## Backend

### Setup & Run

```bash
cd backend
pip install -r ../requirements.txt
# Optional: point at a custom domains file; defaults to ../domains.json in the repo root
# When running on Render with a Secret File named DOMAINS_FILE, it is auto-read from /etc/secrets/DOMAINS_FILE
export DOMAINS_FILE_PATH=../domains.json
uvicorn backend.main:app --reload
```

* Render start command: `uvicorn server:app --host 0.0.0.0 --port $PORT`
* Defaults to `domains.json` in the repo root or `/etc/secrets/DOMAINS_FILE` when provided as a Secret File; override with `DOMAINS_FILE_PATH` for your own list.

### Endpoints

- `GET /domains` — list monitored domains (filterable via `q`).
- `GET /domains/{id}/careers` — preview discovered careers URLs for a domain.
- `POST /run?domainId=<id>` — trigger crawl (full or single domain) as a background task.
- `GET /status` — current crawl status.
- `GET /results?hubspotOnly=true&limit=200` — latest jobs.
- `GET /logs` — recent crawl logs.

### Quick test script

`backend/test_crawler.py` can be run locally to crawl a few domains from the configured file and print found roles.

## Frontend

### Setup & Run

```bash
cd frontend
npm install
npm run dev
```

Set `VITE_API_BASE` to point at the backend URL (defaults to `http://localhost:8000`).

The dashboard lets you trigger crawls, preview careers pages, export jobs to CSV, inspect per-company logs, and view live status with health indicators. It polls backend state to stay in sync.

## Deployment

- Build command: `./postinstall.sh` (install dependencies; add frontend build if desired)
- Start command: `uvicorn server:app --host 0.0.0.0 --port $PORT` (import shim for Render defaults; `backend.main:app` also works)

If using a Render Secret File named `DOMAINS_FILE`, it will be mounted at `/etc/secrets/DOMAINS_FILE` and is read automatically without additional configuration.

The backend listens on the `PORT` environment variable for Render compatibility.
