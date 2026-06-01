from __future__ import annotations

import datetime as dt
from typing import Optional

from sqlalchemy import (
    Column,
    DateTime,
    Enum,
    Float,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from config.settings import ApplicationStatus, DatabaseConfig


class Base(DeclarativeBase):
    pass


class JobApplication(Base):
    __tablename__ = "job_applications"

    id: Optional[int] = Column(Integer, primary_key=True, autoincrement=True)
    job_id: str = Column(String(128), unique=True, index=True)
    title: str = Column(String(512))
    company: str = Column(String(256))
    location: str = Column(String(256))
    platform: str = Column(String(64))
    work_style: str = Column(String(64), default="remote")
    url: str = Column(Text, default="")
    external_url: str = Column(Text, default="")

    # Scoring
    score: float = Column(Float, default=0.0)
    confidence: float = Column(Float, default=0.0)
    decision: str = Column(String(32), default="SKIP")
    reasoning: str = Column(Text, default="")

    # Application details
    resume_used: str = Column(String(512), default="")
    cover_letter_used: str = Column(String(512), default="")
    status: str = Column(String(32), default=ApplicationStatus.APPLIED.value)
    notes: str = Column(Text, default="")

    # Job description
    description: str = Column(Text, default="")
    skills_required: str = Column(Text, default="")  # JSON array
    experience_required: str = Column(String(128), default="")
    salary: str = Column(String(128), default="")

    # Timestamps
    date_posted: str = Column(String(128), default="")
    date_applied: DateTime = Column(DateTime, default=dt.datetime.utcnow)
    date_updated: DateTime = Column(DateTime, default=dt.datetime.utcnow, onupdate=dt.datetime.utcnow)
    date_created: DateTime = Column(DateTime, default=dt.datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "job_id": self.job_id,
            "title": self.title,
            "company": self.company,
            "location": self.location,
            "platform": self.platform,
            "work_style": self.work_style,
            "url": self.url,
            "external_url": self.external_url,
            "score": self.score,
            "confidence": self.confidence,
            "decision": self.decision,
            "reasoning": self.reasoning,
            "resume_used": self.resume_used,
            "cover_letter_used": self.cover_letter_used,
            "status": self.status,
            "notes": self.notes,
            "skills_required": self.skills_required,
            "experience_required": self.experience_required,
            "salary": self.salary,
            "date_posted": self.date_posted,
            "date_applied": self.date_applied.isoformat() if self.date_applied else None,
            "date_updated": self.date_updated.isoformat() if self.date_updated else None,
        }


class JobScore(Base):
    __tablename__ = "job_scores"

    id: Optional[int] = Column(Integer, primary_key=True, autoincrement=True)
    job_id: str = Column(String(128), index=True)
    skill_score: float = Column(Float, default=0.0)
    resume_score: float = Column(Float, default=0.0)
    remote_score: float = Column(Float, default=0.0)
    experience_score: float = Column(Float, default=0.0)
    startup_score: float = Column(Float, default=0.0)
    salary_score: float = Column(Float, default=0.0)
    total_score: float = Column(Float, default=0.0)
    breakdown: str = Column(Text, default="{}")  # JSON breakdown
    created_at: DateTime = Column(DateTime, default=dt.datetime.utcnow)


class GeneratedDocument(Base):
    __tablename__ = "generated_documents"

    id: Optional[int] = Column(Integer, primary_key=True, autoincrement=True)
    job_id: str = Column(String(128), index=True)
    doc_type: str = Column(String(32))  # "resume" or "cover_letter"
    file_path: str = Column(Text)
    content: str = Column(Text, default="")
    model_used: str = Column(String(128), default="")
    created_at: DateTime = Column(DateTime, default=dt.datetime.utcnow)


class DailyReport(Base):
    __tablename__ = "daily_reports"

    id: Optional[int] = Column(Integer, primary_key=True, autoincrement=True)
    report_date: str = Column(String(16), unique=True)
    total_searched: int = Column(Integer, default=0)
    total_ranked: int = Column(Integer, default=0)
    total_applied: int = Column(Integer, default=0)
    total_skipped: int = Column(Integer, default=0)
    total_rejected: int = Column(Integer, default=0)
    avg_score: float = Column(Float, default=0.0)
    platforms_used: str = Column(Text, default="[]")  # JSON
    top_companies: str = Column(Text, default="[]")   # JSON
    report_json: str = Column(Text, default="{}")     # JSON
    created_at: DateTime = Column(DateTime, default=dt.datetime.utcnow)


def init_database(config: DatabaseConfig) -> sessionmaker:
    engine = create_engine(config.url, echo=config.echo)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)
