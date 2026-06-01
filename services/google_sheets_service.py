from __future__ import annotations

import datetime as dt
import json
import logging
from pathlib import Path
from typing import Any

from config.settings import GoogleSheetsConfig

logger = logging.getLogger(__name__)

_gspread = None
_ServiceAccountCredentials = None


def _ensure_imports() -> None:
    global _gspread, _ServiceAccountCredentials
    if _gspread is None:
        import gspread
        from google.oauth2.service_account import Credentials
        _gspread = gspread
        _ServiceAccountCredentials = Credentials


class GoogleSheetsService:
    """Push job application data to a Google Sheets dashboard via service account."""

    SCOPES = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]

    SUMMARY_TAB = "Summary"
    APPLICATIONS_TAB = "Applications"
    DAILY_LOG_TAB = "Daily Log"
    PLATFORM_BREAKDOWN_TAB = "Platform Breakdown"

    SUMMARY_HEADERS = ["Metric", "Value", "Last Updated"]
    APPLICATION_HEADERS = [
        "Job ID", "Title", "Company", "Location", "Platform",
        "Score", "Confidence", "Decision", "Status", "Resume Used",
        "Date Applied", "URL", "Notes",
    ]
    DAILY_LOG_HEADERS = [
        "Date", "Searched", "Ranked", "Applied", "Skipped",
        "Rejected", "Avg Score", "Platforms",
    ]
    PLATFORM_HEADERS = [
        "Platform", "Total Applications", "Interviews", "Offers",
        "Rejections", "Response Rate %",
    ]

    def __init__(self, config: GoogleSheetsConfig) -> None:
        self.config = config
        self._client: Any = None
        self._spreadsheet: Any = None

    def connect(self) -> None:
        if not self.config.enabled:
            return
        if not self.config.spreadsheet_id:
            logger.error("Google Sheets spreadsheet_id not configured")
            return
        creds_path = Path(self.config.credentials_path)
        if not creds_path.exists():
            logger.error("Service account credentials not found at %s", creds_path)
            return
        _ensure_imports()
        creds = _ServiceAccountCredentials.from_service_account_file(
            str(creds_path), scopes=self.SCOPES
        )
        self._client = _gspread.authorize(creds)
        self._spreadsheet = self._client.open_by_key(self.config.spreadsheet_id)
        self._ensure_tabs()
        logger.info("Connected to Google Sheets: %s", self.config.spreadsheet_id)

    def _ensure_tabs(self) -> None:
        if not self._spreadsheet:
            return
        existing = [ws.title for ws in self._spreadsheet.worksheets()]
        tabs = [
            (self.SUMMARY_TAB, self.SUMMARY_HEADERS),
            (self.APPLICATIONS_TAB, self.APPLICATION_HEADERS),
            (self.DAILY_LOG_TAB, self.DAILY_LOG_HEADERS),
            (self.PLATFORM_BREAKDOWN_TAB, self.PLATFORM_HEADERS),
        ]
        for tab_name, headers in tabs:
            if tab_name not in existing:
                ws = self._spreadsheet.add_worksheet(title=tab_name, rows=100, cols=len(headers))
                ws.update(range_name="A1", values=[headers])
                logger.info("Created Google Sheets tab: %s", tab_name)

    def sync_summary(self, stats: dict) -> None:
        if not self._spreadsheet:
            return
        now = dt.datetime.now().isoformat()
        rows = [
            ["Total Applications", stats.get("total_applications", 0), now],
            ["Applications Today", stats.get("applications_today", 0), now],
            ["Response Rate %", stats.get("response_rate", 0), now],
            ["Interviews", stats.get("status_counts", {}).get("Interview", 0), now],
            ["Offers", stats.get("status_counts", {}).get("Offer", 0), now],
            ["Rejections", stats.get("status_counts", {}).get("Rejected", 0), now],
            ["Avg Score", stats.get("score_distribution", {}).get("avg_score", 0), now],
        ]
        ws = self._spreadsheet.worksheet(self.SUMMARY_TAB)
        ws.clear()
        ws.update(range_name="A1", values=[self.SUMMARY_HEADERS])
        ws.update(range_name="A2", values=rows)
        logger.info("Synced summary to Google Sheets")

    def sync_applications(self, applications: list[dict]) -> None:
        if not self._spreadsheet:
            return
        ws = self._spreadsheet.worksheet(self.APPLICATIONS_TAB)
        ws.clear()
        ws.update(range_name="A1", values=[self.APPLICATION_HEADERS])
        if not applications:
            return
        rows = []
        for app in applications:
            rows.append([
                app.get("job_id", ""),
                app.get("title", ""),
                app.get("company", ""),
                app.get("location", ""),
                app.get("platform", ""),
                app.get("score", 0),
                app.get("confidence", 0),
                app.get("decision", ""),
                app.get("status", ""),
                app.get("resume_used", ""),
                app.get("date_applied", ""),
                app.get("url", ""),
                app.get("notes", ""),
            ])
        ws.update(range_name="A2", values=rows)
        logger.info("Synced %d applications to Google Sheets", len(rows))

    def sync_daily_log(self, reports: list[dict]) -> None:
        if not self._spreadsheet:
            return
        ws = self._spreadsheet.worksheet(self.DAILY_LOG_TAB)
        ws.clear()
        ws.update(range_name="A1", values=[self.DAILY_LOG_HEADERS])
        if not reports:
            return
        rows = []
        for r in reports:
            rows.append([
                r.get("report_date", ""),
                r.get("total_searched", 0),
                r.get("total_ranked", 0),
                r.get("total_applied", 0),
                r.get("total_skipped", 0),
                r.get("total_rejected", 0),
                r.get("avg_score", 0),
                r.get("platforms_used", ""),
            ])
        ws.update(range_name="A2", values=rows)
        logger.info("Synced %d daily reports to Google Sheets", len(rows))

    def sync_platform_breakdown(self, platform_stats: dict[str, dict]) -> None:
        if not self._spreadsheet:
            return
        ws = self._spreadsheet.worksheet(self.PLATFORM_BREAKDOWN_TAB)
        ws.clear()
        ws.update(range_name="A1", values=[self.PLATFORM_HEADERS])
        if not platform_stats:
            return
        rows = []
        for platform, data in platform_stats.items():
            rows.append([
                platform,
                data.get("total", 0),
                data.get("interviews", 0),
                data.get("offers", 0),
                data.get("rejections", 0),
                data.get("response_rate", 0),
            ])
        ws.update(range_name="A2", values=rows)
        logger.info("Synced platform breakdown to Google Sheets")

    def sync_all(self, stats: dict, applications: list[dict],
                 reports: list[dict], platform_stats: dict) -> None:
        self.sync_summary(stats)
        self.sync_applications(applications)
        self.sync_daily_log(reports)
        self.sync_platform_breakdown(platform_stats)
        logger.info("Full Google Sheets sync completed")
