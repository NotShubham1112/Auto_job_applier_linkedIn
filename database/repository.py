from __future__ import annotations

import datetime as dt
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from config.settings import ApplicationStatus
from database.models import (
    DailyReport,
    GeneratedDocument,
    JobApplication,
    JobScore,
)


class Repository:
    """Data access layer for all database operations."""

    def __init__(self, session: Session) -> None:
        self.session = session

    # ------------------------------------------------------------------
    # JobApplication
    # ------------------------------------------------------------------

    def get_application_by_job_id(self, job_id: str) -> Optional[JobApplication]:
        return self.session.query(JobApplication).filter_by(job_id=job_id).first()

    def application_exists(self, job_id: str) -> bool:
        return self.get_application_by_job_id(job_id) is not None

    def create_application(self, **kwargs) -> JobApplication:
        app = JobApplication(**kwargs)
        self.session.add(app)
        self.session.commit()
        self.session.refresh(app)
        return app

    def update_application(self, job_id: str, **kwargs) -> Optional[JobApplication]:
        app = self.get_application_by_job_id(job_id)
        if not app:
            return None
        for key, value in kwargs.items():
            if hasattr(app, key):
                setattr(app, key, value)
        app.date_updated = dt.datetime.utcnow()
        self.session.commit()
        self.session.refresh(app)
        return app

    def get_all_applications(self, limit: int = 500) -> list[JobApplication]:
        return (
            self.session.query(JobApplication)
            .order_by(JobApplication.date_applied.desc())
            .limit(limit)
            .all()
        )

    def get_applications_by_status(self, status: ApplicationStatus) -> list[JobApplication]:
        return (
            self.session.query(JobApplication)
            .filter_by(status=status.value)
            .order_by(JobApplication.date_applied.desc())
            .all()
        )

    def get_applications_by_platform(self, platform: str) -> list[JobApplication]:
        return (
            self.session.query(JobApplication)
            .filter_by(platform=platform)
            .order_by(JobApplication.date_applied.desc())
            .all()
        )

    def get_today_applications(self) -> list[JobApplication]:
        today = dt.date.today()
        return (
            self.session.query(JobApplication)
            .filter(func.date(JobApplication.date_applied) == today)
            .order_by(JobApplication.date_applied.desc())
            .all()
        )

    def count_applications(self) -> int:
        return self.session.query(JobApplication).count()

    def count_today_applications(self) -> int:
        today = dt.date.today()
        return (
            self.session.query(JobApplication)
            .filter(func.date(JobApplication.date_applied) == today)
            .count()
        )

    def get_score_distribution(self) -> dict:
        results = (
            self.session.query(
                func.count(JobApplication.id),
                func.avg(JobApplication.score),
            )
            .first()
        )
        return {"total": results[0] or 0, "avg_score": round(results[1] or 0, 2)}

    def get_platform_breakdown(self) -> dict[str, int]:
        rows = (
            self.session.query(JobApplication.platform, func.count(JobApplication.id))
            .group_by(JobApplication.platform)
            .all()
        )
        return {row[0]: row[1] for row in rows}

    def get_status_counts(self) -> dict[str, int]:
        rows = (
            self.session.query(JobApplication.status, func.count(JobApplication.id))
            .group_by(JobApplication.status)
            .all()
        )
        return {row[0]: row[1] for row in rows}

    def get_response_rate(self) -> float:
        total = self.count_applications()
        if total == 0:
            return 0.0
        responded = (
            self.session.query(JobApplication)
            .filter(
                JobApplication.status.in_([
                    ApplicationStatus.INTERVIEW.value,
                    ApplicationStatus.OFFER.value,
                    ApplicationStatus.REJECTED.value,
                ])
            )
            .count()
        )
        return round(responded / total * 100, 2)

    # ------------------------------------------------------------------
    # JobScore
    # ------------------------------------------------------------------

    def create_score(self, **kwargs) -> JobScore:
        score = JobScore(**kwargs)
        self.session.add(score)
        self.session.commit()
        self.session.refresh(score)
        return score

    def get_score_by_job_id(self, job_id: str) -> Optional[JobScore]:
        return self.session.query(JobScore).filter_by(job_id=job_id).first()

    # ------------------------------------------------------------------
    # GeneratedDocument
    # ------------------------------------------------------------------

    def create_document(self, **kwargs) -> GeneratedDocument:
        doc = GeneratedDocument(**kwargs)
        self.session.add(doc)
        self.session.commit()
        self.session.refresh(doc)
        return doc

    def get_documents_by_job_id(self, job_id: str) -> list[GeneratedDocument]:
        return self.session.query(GeneratedDocument).filter_by(job_id=job_id).all()

    def get_latest_resume_for_job(self, job_id: str) -> Optional[GeneratedDocument]:
        return (
            self.session.query(GeneratedDocument)
            .filter_by(job_id=job_id, doc_type="resume")
            .order_by(GeneratedDocument.created_at.desc())
            .first()
        )

    # ------------------------------------------------------------------
    # DailyReport
    # ------------------------------------------------------------------

    def create_daily_report(self, **kwargs) -> DailyReport:
        report = DailyReport(**kwargs)
        self.session.add(report)
        self.session.commit()
        self.session.refresh(report)
        return report

    def get_daily_report(self, date_str: str) -> Optional[DailyReport]:
        return self.session.query(DailyReport).filter_by(report_date=date_str).first()

    def get_recent_reports(self, days: int = 30) -> list[DailyReport]:
        cutoff = dt.date.today() - dt.timedelta(days=days)
        return (
            self.session.query(DailyReport)
            .filter(DailyReport.report_date >= cutoff.isoformat())
            .order_by(DailyReport.report_date.desc())
            .all()
        )

    # ------------------------------------------------------------------
    # Aggregates for dashboard
    # ------------------------------------------------------------------

    def get_dashboard_stats(self) -> dict:
        return {
            "total_applications": self.count_applications(),
            "applications_today": self.count_today_applications(),
            "response_rate": self.get_response_rate(),
            "status_counts": self.get_status_counts(),
            "platform_breakdown": self.get_platform_breakdown(),
            "score_distribution": self.get_score_distribution(),
        }
