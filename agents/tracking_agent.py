from __future__ import annotations

import datetime as dt
import json
import logging
from typing import Any

from config.settings import AppConfig, ApplicationStatus
from database.repository import Repository
from services.google_sheets_service import GoogleSheetsService

logger = logging.getLogger(__name__)


class TrackingAgent:
    """Tracks all applications, generates reports, and syncs to Google Sheets."""

    def __init__(
        self,
        config: AppConfig,
        repo: Repository,
        sheets_service: GoogleSheetsService | None = None,
    ) -> None:
        self.config = config
        self.repo = repo
        self.sheets = sheets_service

    def record_application(
        self,
        job: dict[str, Any],
        ranking: dict[str, Any],
        decision: dict[str, Any],
        resume_path: str = "",
        cover_letter_path: str = "",
    ) -> None:
        """Store a completed application in the database."""
        try:
            self.repo.create_application(
                job_id=job.get("job_id", ""),
                title=job.get("title", ""),
                company=job.get("company", ""),
                location=job.get("location", ""),
                platform=job.get("platform", ""),
                work_style=job.get("work_style", ""),
                url=job.get("url", ""),
                external_url=job.get("external_url", ""),
                score=ranking.get("score", 0),
                confidence=decision.get("confidence", 0),
                decision=decision.get("decision", "SKIP"),
                reasoning=decision.get("reasoning", ""),
                resume_used=resume_path,
                cover_letter_used=cover_letter_path,
                status=ApplicationStatus.APPLIED.value,
                description=job.get("description", ""),
                skills_required=json.dumps(job.get("skills_required", [])),
                experience_required=job.get("experience_required", ""),
                salary=job.get("salary", ""),
                date_posted=job.get("date_posted", ""),
            )
            logger.info(
                "TrackingAgent: recorded application for %s at %s (score: %.1f)",
                job.get("title"), job.get("company"), ranking.get("score", 0),
            )
        except Exception as e:
            logger.error("TrackingAgent: failed to record application: %s", e)

    def update_status(self, job_id: str, status: ApplicationStatus, notes: str = "") -> None:
        try:
            self.repo.update_application(
                job_id=job_id,
                status=status.value,
                notes=notes,
            )
            logger.info("TrackingAgent: updated %s to %s", job_id, status.value)
        except Exception as e:
            logger.error("TrackingAgent: failed to update %s: %s", job_id, e)

    def generate_daily_report(self) -> dict[str, Any]:
        today = dt.date.today().isoformat()
        apps = self.repo.get_today_applications()
        stats = self.repo.get_dashboard_stats()

        report = {
            "report_date": today,
            "total_searched": len(apps),
            "total_ranked": len(apps),
            "total_applied": sum(1 for a in apps if a.decision == "APPLY"),
            "total_skipped": sum(1 for a in apps if a.decision == "SKIP"),
            "total_rejected": sum(1 for a in apps if a.status == ApplicationStatus.REJECTED.value),
            "avg_score": (
                sum(a.score for a in apps) / len(apps) if apps else 0
            ),
            "platforms_used": json.dumps(list(stats.get("platform_breakdown", {}).keys())),
            "top_companies": json.dumps(
                list(set(a.company for a in apps))[:10]
            ),
            "report_json": json.dumps(stats),
        }

        try:
            existing = self.repo.get_daily_report(today)
            if existing:
                # Update existing report
                for key, value in report.items():
                    if key != "report_date" and hasattr(existing, key):
                        setattr(existing, key, value)
                self.repo.session.commit()
            else:
                self.repo.create_daily_report(**report)
        except Exception as e:
            logger.warning("TrackingAgent: failed to store daily report: %s", e)

        return report

    def sync_to_sheets(self) -> None:
        if not self.sheets or not self.config.google_sheets.enabled:
            return
        try:
            stats = self.repo.get_dashboard_stats()
            apps = [a.to_dict() for a in self.repo.get_all_applications()]
            reports = [
                {
                    "report_date": r.report_date,
                    "total_searched": r.total_searched,
                    "total_ranked": r.total_ranked,
                    "total_applied": r.total_applied,
                    "total_skipped": r.total_skipped,
                    "total_rejected": r.total_rejected,
                    "avg_score": r.avg_score,
                    "platforms_used": r.platforms_used,
                }
                for r in self.repo.get_recent_reports()
            ]
            # Build platform stats
            platform_breakdown = stats.get("platform_breakdown", {})
            platform_stats = {}
            for platform, count in platform_breakdown.items():
                platform_stats[platform] = {
                    "total": count,
                    "interviews": 0,
                    "offers": 0,
                    "rejections": 0,
                    "response_rate": 0,
                }
            self.sheets.sync_all(stats, apps, reports, platform_stats)
        except Exception as e:
            logger.error("TrackingAgent: failed to sync to Google Sheets: %s", e)

    def get_dashboard_data(self) -> dict[str, Any]:
        return self.repo.get_dashboard_stats()

    def get_all_applications(self, limit: int = 500) -> list[dict[str, Any]]:
        return [a.to_dict() for a in self.repo.get_all_applications(limit)]
