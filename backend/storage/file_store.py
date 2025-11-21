import json
import os
from typing import Dict, List

from backend.models import JobPosting


def save_jobs_to_file(jobs: List[JobPosting], path: str = "data/jobs-latest.json") -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump([job.dict() for job in jobs], f, ensure_ascii=False, indent=2)


def load_jobs_from_file(path: str = "data/jobs-latest.json") -> Dict[str, JobPosting]:
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return {item["id"]: JobPosting(**item) for item in data}
    except Exception:
        return {}
