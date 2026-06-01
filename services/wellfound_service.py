from __future__ import annotations

import logging
from typing import Any

from config.settings import SearchConfig
from playwright.sync_api import Page

logger = logging.getLogger(__name__)


class WellfoundService:
    """Playwright-based Wellfound job scraper (uses shared browser page)."""

    BASE_URL = "https://wellfound.com/role"

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
                page.wait_for_selector('[data-test="StartupResult"]', timeout=10000)
            except Exception:
                break
            cards = page.query_selector_all('[data-test="StartupResult"]')
            for card in cards:
                try:
                    job = self._parse_card(card)
                    if job:
                        jobs.append(job)
                except Exception as e:
                    logger.warning("Wellfound: failed to parse card: %s", e)

            next_btn = page.query_selector('a[aria-label="Next"]')
            if not next_btn:
                break
            next_btn.click()
            page.wait_for_timeout(2000)

        logger.info("Wellfound: Found %d jobs for '%s'", len(jobs), keyword)
        return jobs

    def _parse_card(self, card: Any) -> dict[str, Any] | None:
        title_el = card.query_selector('div[data-test="RoleInfo"] a')
        company_el = card.query_selector('div[data-test="StartupInfo"] a')
        location_el = card.query_selector('div[data-test="RoleInfo"] span')

        if not title_el:
            return None

        href = title_el.get_attribute("href") or ""
        url = f"https://wellfound.com{href}" if href.startswith("/") else href

        return {
            "job_id": f"wellfound_{href.split('/')[-1] if href else ''}",
            "title": title_el.inner_text().strip(),
            "company": company_el.inner_text().strip() if company_el else "",
            "location": location_el.inner_text().strip() if location_el else "",
            "platform": "wellfound",
            "url": url,
            "date_posted": "",
            "work_style": "remote" if "remote" in (location_el.inner_text() if location_el else "").lower() else "onsite",
        }

    def get_job_description(self, page: Page, url: str) -> str:
        try:
            page.goto(url, wait_until="networkidle", timeout=20000)
            desc_el = page.query_selector('[data-test="RoleDescription"]')
            return desc_el.inner_text().strip() if desc_el else ""
        except Exception as e:
            logger.warning("Wellfound: failed to get description: %s", e)
            return ""
