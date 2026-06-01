from __future__ import annotations

import logging
from typing import Any, Optional

from config.settings import SearchConfig
from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page

logger = logging.getLogger(__name__)


class LinkedInService:
    """Playwright-based LinkedIn job scraper."""

    BASE_URL = "https://www.linkedin.com/jobs/search"

    def __init__(self, search_config: SearchConfig) -> None:
        self.config = search_config

    def search_jobs(self, page: Page, keyword: str, max_pages: int = 5) -> list[dict[str, Any]]:
        url = self._build_search_url(keyword)
        page.goto(url, wait_until="networkidle", timeout=30000)
        jobs: list[dict[str, Any]] = []

        for page_num in range(max_pages):
            try:
                page.wait_for_selector(".job-search-card", timeout=10000)
            except Exception:
                break
            cards = page.query_selector_all(".job-search-card")
            for card in cards:
                try:
                    job = self._parse_job_card(card)
                    if job:
                        jobs.append(job)
                except Exception as e:
                    logger.warning("Failed to parse LinkedIn card: %s", e)

            next_btn = page.query_selector('button[aria-label="Next"]')
            if not next_btn or page_num == max_pages - 1:
                break
            next_btn.click()
            page.wait_for_timeout(2000)

        logger.info("LinkedIn: Found %d jobs for '%s'", len(jobs), keyword)
        return jobs

    def _build_search_url(self, keyword: str) -> str:
        from urllib.parse import quote_plus
        params: dict[str, str] = {"keywords": keyword}
        if self.config.search_location:
            params["location"] = self.config.search_location
        if self.config.easy_apply_only:
            params["f_AL"] = "true"
        if self.config.date_posted:
            date_map = {"past day": "r86400", "past week": "r604800", "past month": "r2592000"}
            if self.config.date_posted in date_map:
                params["f_TPR"] = date_map[self.config.date_posted]
        if self.config.remote_only:
            params["f_WT"] = "2"
        query = "&".join(f"{k}={quote_plus(v)}" for k, v in params.items())
        return f"{self.BASE_URL}?{query}"

    def _parse_job_card(self, card: Any) -> dict[str, Any] | None:
        import re
        title_el = card.query_selector(".base-search-card__title")
        company_el = card.query_selector(".base-search-card__subtitle a")
        location_el = card.query_selector(".job-search-card__location")
        link_el = card.query_selector("a.base-card__full-link")
        date_el = card.query_selector("time")

        if not title_el or not link_el:
            return None

        title = title_el.inner_text().strip()
        company = company_el.inner_text().strip() if company_el else ""
        location = location_el.inner_text().strip() if location_el else ""
        url = (link_el.get_attribute("href") or "").split("?")[0]
        job_id_match = re.search(r"/view/[^/]*-(\d+)", url)
        job_id = job_id_match.group(1) if job_id_match else url
        date_posted = date_el.get_attribute("datetime") if date_el else ""

        return {
            "job_id": f"linkedin_{job_id}",
            "title": title,
            "company": company,
            "location": location,
            "platform": "linkedin",
            "url": url,
            "date_posted": date_posted,
            "work_style": "remote" if "remote" in location.lower() else "onsite",
        }

    def get_job_description(self, page: Page, url: str) -> str:
        try:
            page.goto(url, wait_until="networkidle", timeout=20000)
            desc_el = page.query_selector(".show-more-less-html__markup, .description__text")
            return desc_el.inner_text().strip() if desc_el else ""
        except Exception as e:
            logger.warning("Failed to get LinkedIn description: %s", e)
            return ""
