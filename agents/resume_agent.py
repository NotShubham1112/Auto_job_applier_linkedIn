from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from config.settings import AppConfig
from database.repository import Repository
from services.groq_service import GroqService

logger = logging.getLogger(__name__)


class ResumeAgent:
    """Selects the best resume and optionally tailors the summary per job."""

    # Map role keywords to resume file names
    RESUME_MAP = {
        "ai": "ai.pdf",
        "machine learning": "ml.pdf",
        "ml": "ml.pdf",
        "full stack": "fullstack.pdf",
        "fullstack": "fullstack.pdf",
        "full-stack": "fullstack.pdf",
        "backend": "backend.pdf",
        "research": "research.pdf",
        "frontend": "fullstack.pdf",
    }

    def __init__(self, config: AppConfig, repo: Repository, groq: GroqService) -> None:
        self.config = config
        self.repo = repo
        self.groq = groq
        self._candidate_profile: str = ""

    def set_candidate_profile(self, profile: str) -> None:
        self._candidate_profile = profile

    def select_best_resume(self, job: dict[str, Any]) -> str:
        """Select the best resume file for a given job based on title/description."""
        resumes_dir = Path(self.config.resume.resumes_dir)
        if not resumes_dir.exists():
            logger.warning("ResumeAgent: resumes directory not found at %s", resumes_dir)
            return self.config.resume.default_resume_path

        title_lower = (job.get("title", "") + " " + job.get("description", "")).lower()

        # Try to match role keyword
        for keyword, filename in self.RESUME_MAP.items():
            if keyword in title_lower:
                candidate = resumes_dir / filename
                if candidate.exists():
                    logger.info("ResumeAgent: selected '%s' for job '%s'", filename, job.get("title"))
                    return str(candidate)

        # Fallback to default
        default = Path(self.config.resume.default_resume_path)
        if default.exists():
            return str(default)

        # Fallback to any PDF in resumes dir
        pdfs = list(resumes_dir.glob("*.pdf"))
        if pdfs:
            return str(pdfs[0])

        return self.config.resume.default_resume_path

    def tailor_summary(self, job: dict[str, Any]) -> str:
        """Generate a tailored resume summary for the specific job."""
        if not self.config.ai.use_ai:
            return self.config.resume.linkedin_summary

        try:
            summary = self.groq.generate_resume_summary(
                job_description=job.get("description", ""),
                candidate_profile=self._candidate_profile,
                job_title=job.get("title", ""),
                company=job.get("company", ""),
            )
            logger.info("ResumeAgent: tailored summary for '%s'", job.get("title"))
            return summary
        except Exception as e:
            logger.warning("ResumeAgent: failed to tailor summary: %s", e)
            return self.config.resume.linkedin_summary

    def get_candidate_profile(self) -> str:
        return self._candidate_profile
