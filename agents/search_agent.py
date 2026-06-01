from __future__ import annotations

import logging
from typing import Any

from config.settings import AppConfig, JobPlatform
from database.repository import Repository
from services.linkedin_service import LinkedInService
from services.wellfound_service import WellfoundService
from services.yc_jobs_service import YCJobsService
from services.remoteok_service import RemoteOKService

logger = logging.getLogger(__name__)


class SearchAgent:
    """Collects jobs from multiple platforms using a shared browser."""

    def __init__(self, config: AppConfig, repo: Repository) -> None:
        self.config = config
        self.repo = repo
        self._services: dict[str, Any] = {}
        self._pw: Any = None
        self._browser: Any = None
        self._page: Any = None

    def _ensure_browser(self) -> None:
        if self._page is None or self._page.is_closed():
            from playwright.sync_api import sync_playwright
            self._pw = sync_playwright().start()
            self._browser = self._pw.chromium.launch(
                headless=self.config.browser.run_in_background,
                args=["--disable-blink-features=AutomationControlled"],
            )
            context = self._browser.new_context(
                user_agent=(
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/120.0.0.0 Safari/537.36"
                ),
                viewport={"width": 1920, "height": 1080},
            )
            self._page = context.new_page()

    def _get_service(self, platform: JobPlatform) -> Any:
        if platform.value not in self._services:
            if platform == JobPlatform.LINKEDIN:
                self._services[platform.value] = LinkedInService(self.config.search)
            elif platform == JobPlatform.WELLFOUND:
                self._services[platform.value] = WellfoundService(self.config.search)
            elif platform == JobPlatform.YC_JOBS:
                self._services[platform.value] = YCJobsService(self.config.search)
            elif platform == JobPlatform.REMOTEOK:
                self._services[platform.value] = RemoteOKService(self.config.search)
        return self._services[platform.value]

    def search(self) -> list[dict[str, Any]]:
        all_jobs: list[dict[str, Any]] = []
        platforms = self.config.search.platforms or [JobPlatform.LINKEDIN]

        for keyword in self.config.search.search_terms:
            for platform in platforms:
                try:
                    # Recreate browser if it crashed
                    if platform != JobPlatform.REMOTEOK:
                        self._ensure_browser()
                    service = self._get_service(platform)
                    if platform == JobPlatform.REMOTEOK:
                        jobs = service.search_jobs(keyword)
                    else:
                        jobs = service.search_jobs(self._page, keyword)
                    all_jobs.extend(jobs)
                    logger.info(
                        "SearchAgent: %d jobs from %s for '%s'",
                        len(jobs), platform.value, keyword,
                    )
                except Exception as e:
                    logger.error("SearchAgent: %s error for '%s': %s", platform.value, keyword, e)
                    # Reset browser on crash
                    if "closed" in str(e).lower() or "target" in str(e).lower():
                        self._reset_browser()

        # Deduplicate by job_id
        seen: set[str] = set()
        unique: list[dict[str, Any]] = []
        for job in all_jobs:
            if job["job_id"] not in seen:
                seen.add(job["job_id"])
                unique.append(job)

        # Filter out already applied jobs
        fresh: list[dict[str, Any]] = []
        for job in unique:
            if not self.repo.application_exists(job["job_id"]):
                fresh.append(job)

        logger.info(
            "SearchAgent: %d unique new jobs (filtered %d duplicates + %d already applied)",
            len(fresh),
            len(unique) - len(fresh),
            len(all_jobs) - len(unique),
        )
        return fresh

    def enrich_job(self, job: dict[str, Any]) -> dict[str, Any]:
        """Fetch full job description — skip for LinkedIn (anti-bot), only for other platforms."""
        if job.get("description"):
            return job
        platform = job.get("platform", "")
        url = job.get("url", "")
        if not url or platform in ("remoteok", "linkedin"):
            return job
        try:
            self._ensure_browser()
            service = self._get_service(JobPlatform(platform))
            job["description"] = service.get_job_description(self._page, url)
        except Exception as e:
            logger.warning("SearchAgent: failed to enrich job %s: %s", job.get("job_id"), e)
        return job

    def cleanup(self) -> None:
        if self._browser:
            self._browser.close()
        if self._pw:
            self._pw.stop()
        self._page = None
        self._browser = None
        self._pw = None
        self._services.clear()

    def _reset_browser(self) -> None:
        """Close and clear browser state so it gets recreated on next use."""
        try:
            if self._browser:
                self._browser.close()
        except Exception:
            pass
        try:
            if self._pw:
                self._pw.stop()
        except Exception:
            pass
        self._page = None
        self._browser = None
        self._pw = None
