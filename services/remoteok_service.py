from __future__ import annotations

import logging
from typing import Any

import httpx

from config.settings import SearchConfig

logger = logging.getLogger(__name__)


class RemoteOKService:
    """API-based RemoteOK job scraper (no browser needed)."""

    BASE_URL = "https://remoteok.com/api"

    def __init__(self, search_config: SearchConfig) -> None:
        self.config = search_config

    def search_jobs(self, keyword: str, max_pages: int = 1) -> list[dict[str, Any]]:
        try:
            resp = httpx.get(self.BASE_URL, timeout=15, headers={"User-Agent": "JobAgent/1.0"})
            resp.raise_for_status()
            raw_jobs = resp.json()
        except Exception as e:
            logger.error("RemoteOK API error: %s", e)
            return []

        # RemoteOK returns a list; first item is metadata
        if raw_jobs and isinstance(raw_jobs[0], dict) and "legal" in raw_jobs[0]:
            raw_jobs = raw_jobs[1:]

        keyword_lower = keyword.lower()
        jobs: list[dict[str, Any]] = []
        for item in raw_jobs:
            if not isinstance(item, dict):
                continue
            title = item.get("position", "")
            tags = " ".join(item.get("tags", [])).lower()
            if keyword_lower not in title.lower() and keyword_lower not in tags:
                continue
            jobs.append(self._normalize(item))
            if len(jobs) >= max_pages * 50:
                break

        logger.info("RemoteOK: Found %d jobs for '%s'", len(jobs), keyword)
        return jobs

    def _normalize(self, item: dict) -> dict[str, Any]:
        job_id = str(item.get("id", ""))
        return {
            "job_id": f"remoteok_{job_id}",
            "title": item.get("position", ""),
            "company": item.get("company", ""),
            "location": item.get("location", "Remote"),
            "platform": "remoteok",
            "url": f"https://remoteok.com/remote-jobs/{job_id}",
            "date_posted": item.get("date", ""),
            "work_style": "remote",
            "salary_min": item.get("salary_min"),
            "salary_max": item.get("salary_max"),
            "description": "",
        }

    def get_job_description(self, url: str) -> str:
        try:
            resp = httpx.get(url, timeout=15, headers={"User-Agent": "JobAgent/1.0"})
            resp.raise_for_status()
            # Simple extraction from page content
            text = resp.text
            # Look for description in meta or content
            import re
            match = re.search(r'<div class="content"[^>]*>(.*?)</div>', text, re.DOTALL)
            if match:
                raw = match.group(1)
                clean = re.sub(r"<[^>]+>", " ", raw)
                return " ".join(clean.split()).strip()
            return ""
        except Exception as e:
            logger.warning("RemoteOK: failed to get description: %s", e)
            return ""
