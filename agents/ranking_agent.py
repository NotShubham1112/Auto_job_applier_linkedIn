from __future__ import annotations

import json
import logging
import re
from typing import Any

from config.settings import AppConfig
from database.repository import Repository
from services.groq_service import GroqService

logger = logging.getLogger(__name__)


class RankingAgent:
    """Scores jobs 0-100 based on skill match, resume match, and other factors."""

    # Keywords for rule-based pre-scoring
    AI_KEYWORDS = {
        "ai", "artificial intelligence", "machine learning", "deep learning",
        "nlp", "natural language processing", "llm", "large language model",
        "rag", "retrieval augmented generation", "agent", "agentic",
        "generative ai", "gen ai", "transformer", "neural network",
    }
    FULLSTACK_KEYWORDS = {
        "full stack", "fullstack", "full-stack", "react", "next.js", "nextjs",
        "vue", "angular", "node.js", "nodejs", "fastapi", "django", "flask",
    }
    STARTUP_KEYWORDS = {
        "startup", "founding engineer", "founding team", "early stage",
        "series a", "seed", "yc", "y combinator", "seed round",
    }

    def __init__(self, config: AppConfig, repo: Repository, groq: GroqService) -> None:
        self.config = config
        self.repo = repo
        self.groq = groq
        self.rc = config.ranking

    def rank(self, job: dict[str, Any], candidate_profile: str) -> dict[str, Any]:
        """Score a single job. Returns ranking dict with total_score 0-100."""
        # --- Rule-based component ---
        desc_lower = (job.get("description", "") + " " + job.get("title", "")).lower()
        skills_lower = " ".join(job.get("skills_required", [])).lower() if isinstance(job.get("skills_required"), list) else str(job.get("skills_required", "")).lower()

        skill_score = self._skill_match_score(desc_lower, skills_lower)
        remote_score = self._remote_score(job)
        experience_score = self._experience_score(job)
        startup_score = self._startup_score(desc_lower)
        salary_score = self._salary_score(job)
        resume_score = 50.0  # Default mid score; AI can refine

        # AI-based refinement (optional)
        if self.config.ai.use_ai:
            try:
                ai_result = self.groq.rank_job(job, candidate_profile)
                ai_score = ai_result.get("score", 50)
                resume_score = ai_result.get("resume_match", 50)
                # Blend rule-based (40%) with AI (60%)
                total = (
                    skill_score * 0.20
                    + resume_score * 0.25
                    + remote_score * 0.15
                    + experience_score * 0.15
                    + startup_score * 0.15
                    + salary_score * 0.10
                )
                total = total * 0.4 + ai_score * 0.6
            except Exception as e:
                logger.warning("RankingAgent: AI ranking failed, using rule-based: %s", e)
                total = self._compute_rule_total(
                    skill_score, resume_score, remote_score, experience_score, startup_score, salary_score
                )
        else:
            total = self._compute_rule_total(
                skill_score, resume_score, remote_score, experience_score, startup_score, salary_score
            )

        total = max(0.0, min(100.0, total))

        # Check auto-reject
        for keyword in self.rc.auto_reject_keywords:
            if keyword in desc_lower:
                total = 0.0
                break

        ranking = {
            "skill_match": round(skill_score, 1),
            "resume_match": round(resume_score, 1),
            "remote_match": round(remote_score, 1),
            "experience_match": round(experience_score, 1),
            "startup_match": round(startup_score, 1),
            "salary_match": round(salary_score, 1),
            "score": round(total, 1),
        }

        # Store in DB
        try:
            self.repo.create_score(
                job_id=job.get("job_id", ""),
                skill_score=ranking["skill_match"],
                resume_score=ranking["resume_match"],
                remote_score=ranking["remote_match"],
                experience_score=ranking["experience_match"],
                startup_score=ranking["startup_match"],
                salary_score=ranking["salary_match"],
                total_score=ranking["score"],
                breakdown=json.dumps(ranking),
            )
        except Exception as e:
            logger.warning("RankingAgent: failed to store score: %s", e)

        return ranking

    def _compute_rule_total(
        self, skill: float, resume: float, remote: float,
        experience: float, startup: float, salary: float,
    ) -> float:
        w = self.rc
        return (
            skill * w.skill_match_weight * 100
            + resume * w.resume_match_weight * 100
            + remote * w.remote_preference_weight * 100
            + experience * w.experience_match_weight * 100
            + startup * w.startup_quality_weight * 100
            + salary * w.salary_weight * 100
        )

    def _skill_match_score(self, desc: str, skills: str) -> float:
        text = desc + " " + skills
        matches = sum(1 for kw in self.AI_KEYWORDS if kw in text)
        fs_matches = sum(1 for kw in self.FULLSTACK_KEYWORDS if kw in text)
        # Normalize: 5+ AI keywords = full score
        score = min(matches / 5.0, 1.0) * 0.7 + min(fs_matches / 3.0, 1.0) * 0.3
        return score

    def _remote_score(self, job: dict) -> float:
        style = job.get("work_style", "").lower()
        location = job.get("location", "").lower()
        if "remote" in style or "remote" in location:
            return 1.0
        if "hybrid" in style or "hybrid" in location:
            return 0.5
        return 0.2

    def _experience_score(self, job: dict) -> float:
        desc = job.get("description", "").lower()
        exp_req = job.get("experience_required", "")
        current = self.config.search.current_experience
        max_req = self.config.search.max_experience_required

        # Try to extract years from description
        match = re.search(r"(\d+)\+?\s*(?:years?|yrs?)", desc)
        if match:
            required = int(match.group(1))
            if max_req > 0 and required > max_req:
                return 0.1
            if required <= current + 1:
                return 1.0
            if required <= current + 3:
                return 0.7
            return 0.3
        return 0.6  # Unknown = moderate score

    def _startup_score(self, desc: str) -> float:
        matches = sum(1 for kw in self.STARTUP_KEYWORDS if kw in desc)
        return min(matches / 2.0, 1.0)

    def _salary_score(self, job: dict) -> float:
        salary = job.get("salary", "")
        if not salary:
            return 0.5  # Unknown
        # Try to extract numbers
        nums = re.findall(r"\d+", salary.replace(",", ""))
        if not nums:
            return 0.5
        max_val = max(int(n) for n in nums)
        if max_val >= 150000:
            return 1.0
        if max_val >= 100000:
            return 0.8
        if max_val >= 60000:
            return 0.6
        return 0.3

    def filter_jobs(self, jobs: list[dict[str, Any]], rankings: list[dict[str, Any]]) -> list[tuple[dict, dict]]:
        """Return only jobs that pass the threshold, paired with their ranking."""
        passed: list[tuple[dict, dict]] = []
        for job, ranking in zip(jobs, rankings):
            if ranking["score"] >= self.rc.min_score_threshold:
                passed.append((job, ranking))
            else:
                logger.info(
                    "RankingAgent: SKIP %s at %s (score %.1f < %d)",
                    job.get("title"), job.get("company"),
                    ranking["score"], self.rc.min_score_threshold,
                )
        return passed
