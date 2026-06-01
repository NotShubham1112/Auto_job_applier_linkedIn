from __future__ import annotations

import logging
from typing import Any

from config.settings import SearchConfig
from playwright.sync_api import Page

logger = logging.getLogger(__name__)


class YCJobsService:
    """Playwright-based YC Work at a Startup scraper (uses shared browser page)."""

    BASE_URL = "https://www.workatastartup.com/jobs"

    def __init__(self, search_config: SearchConfig) -> None:
        self.config = search_config

    def search_jobs(self, page: Page, keyword: str, max_pages: int = 3) -> list[dict[str, Any]]:
        url = f"{self.BASE_URL}?q={keyword}"
        if self.config.remote_only:
            url += "&remote=true"
        page.goto(url, wait_until="networkidle", timeout=30000)
        jobs: list[dict[str, Any]] = []

        for _ in range(max_pages):
            try:
                page.wait_for_selector(".job-listing", timeout=10000)
            except Exception:
                break
            cards = page.query_selector_all(".job-listing")
            for card in cards:
                try:
                    job = self._parse_card(card)
                    if job:
                        jobs.append(job)
                except Exception as e:
                    logger.warning("YC Jobs: failed to parse card: %s", e)

            next_btn = page.query_selector('a:has-text("Next")')
            if not next_btn:
                break
            next_btn.click()
            page.wait_for_timeout(2000)

        logger.info("YC Jobs: Found %d jobs for '%s'", len(jobs), keyword)
        return jobs

    def _parse_card(self, card: Any) -> dict[str, Any] | None:
        title_el = card.query_selector("h4, .job-title, a")
        company_el = card.query_selector(".company-name, .startup-name")

        if not title_el:
            return None

        href = title_el.get_attribute("href") or ""
        url = f"https://www.workatastartup.com{href}" if href.startswith("/") else href

        return {
            "job_id": f"yc_{href.split('/')[-1] if href else ''}",
            "title": title_el.inner_text().strip(),
            "company": company_el.inner_text().strip() if company_el else "",
            "location": "Remote",
            "platform": "yc_jobs",
            "url": url,
            "date_posted": "",
            "work_style": "remote",
        }

    def get_job_description(self, page: Page, url: str) -> str:
        try:
            page.goto(url, wait_until="networkidle", timeout=20000)
            desc_el = page.query_selector(".job-description, .role-description, article")
            return desc_el.inner_text().strip() if desc_el else ""
        except Exception as e:
            logger.warning("YC Jobs: failed to get description: %s", e)
            return ""
