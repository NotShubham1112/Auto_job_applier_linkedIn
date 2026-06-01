from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from config.settings import AppConfig
from database.repository import Repository
from services.groq_service import GroqService

logger = logging.getLogger(__name__)


class CoverLetterAgent:
    """Generates company-specific cover letters using Groq."""

    def __init__(self, config: AppConfig, repo: Repository, groq: GroqService) -> None:
        self.config = config
        self.repo = repo
        self.groq = groq
        self._candidate_profile: str = ""

    def set_candidate_profile(self, profile: str) -> None:
        self._candidate_profile = profile

    def generate(self, job: dict[str, Any]) -> str:
        """Generate a cover letter for the given job."""
        if not self.config.ai.use_ai:
            return self.config.resume.cover_letter

        try:
            cover_letter = self.groq.generate_cover_letter(
                job_description=job.get("description", ""),
                candidate_profile=self._candidate_profile,
                job_title=job.get("title", ""),
                company=job.get("company", ""),
            )
            logger.info("CoverLetterAgent: generated for '%s' at '%s'", job.get("title"), job.get("company"))
            return cover_letter
        except Exception as e:
            logger.warning("CoverLetterAgent: generation failed: %s", e)
            return self.config.resume.cover_letter

    def save(self, job: dict[str, Any], content: str) -> str:
        """Save generated cover letter to file. Returns file path."""
        output_dir = Path(self.config.resume.generated_resume_path)
        output_dir.mkdir(parents=True, exist_ok=True)

        company = job.get("company", "unknown").replace(" ", "_").replace("|", "").lower()
        title = job.get("title", "unknown").replace(" ", "_").replace("|", "").lower()
        filename = f"cover_letter_{company}_{title}.txt"
        filepath = output_dir / filename

        filepath.write_text(content, encoding="utf-8")
        logger.info("CoverLetterAgent: saved to %s", filepath)

        # Store in DB
        try:
            self.repo.create_document(
                job_id=job.get("job_id", ""),
                doc_type="cover_letter",
                file_path=str(filepath),
                content=content,
                model_used=self.config.ai.groq_model.value,
            )
        except Exception as e:
            logger.warning("CoverLetterAgent: failed to store in DB: %s", e)

        return str(filepath)
