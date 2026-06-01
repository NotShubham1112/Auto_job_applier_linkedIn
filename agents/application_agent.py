from __future__ import annotations

import logging
from typing import Any

from config.settings import AppConfig, ApplicationDecision
from database.repository import Repository
from services.groq_service import GroqService

logger = logging.getLogger(__name__)


class ApplicationAgent:
    """Makes intelligent APPLY / SKIP / REVIEW decisions before submitting."""

    def __init__(self, config: AppConfig, repo: Repository, groq: GroqService) -> None:
        self.config = config
        self.repo = repo
        self.groq = groq
        self._candidate_profile: str = ""

    def set_candidate_profile(self, profile: str) -> None:
        self._candidate_profile = profile

    def decide(self, job: dict[str, Any], ranking: dict[str, Any]) -> dict[str, Any]:
        """Analyze job + ranking and return a decision with reasoning."""
        decision_text = "SKIP"
        confidence = 0.0
        reasoning = ""

        # Quick rule-based gate
        score = ranking.get("score", 0)
        if score < self.config.ranking.min_score_threshold:
            return {
                "decision": ApplicationDecision.SKIP.value,
                "confidence": 0.9,
                "reasoning": f"Score {score} below threshold {self.config.ranking.min_score_threshold}",
            }

        # AI-powered decision
        if self.config.ai.use_ai:
            try:
                result = self.groq.decide_application(
                    job_data=job,
                    ranking=ranking,
                    candidate_profile=self._candidate_profile,
                )
                decision_text = result.get("decision", "REVIEW").upper()
                confidence = float(result.get("confidence", 0.5))
                reasoning = result.get("reasoning", "")

                # Validate decision value
                if decision_text not in [d.value for d in ApplicationDecision]:
                    decision_text = "REVIEW"

            except Exception as e:
                logger.warning("ApplicationAgent: AI decision failed: %s", e)
                # Fallback: high score = apply
                if score >= 80:
                    decision_text = "APPLY"
                    confidence = 0.7
                    reasoning = f"Fallback: score {score} is high, AI unavailable"
                elif score >= 60:
                    decision_text = "REVIEW"
                    confidence = 0.5
                    reasoning = f"Fallback: score {score} moderate, needs review"
                else:
                    decision_text = "SKIP"
                    confidence = 0.8
                    reasoning = f"Fallback: score {score} too low"
        else:
            # No AI: simple threshold
            if score >= 80:
                decision_text = "APPLY"
                confidence = 0.8
                reasoning = f"Score {score} exceeds high threshold"
            elif score >= 60:
                decision_text = "REVIEW"
                confidence = 0.5
                reasoning = f"Score {score} in review range"
            else:
                decision_text = "SKIP"
                confidence = 0.9
                reasoning = f"Score {score} below threshold"

        # Final confidence gate for APPLY
        if decision_text == "APPLY" and confidence < self.config.ranking.confidence_threshold:
            decision_text = "REVIEW"
            reasoning += f" (confidence {confidence:.2f} below threshold {self.config.ranking.confidence_threshold})"

        return {
            "decision": decision_text,
            "confidence": round(confidence, 3),
            "reasoning": reasoning,
        }

    def should_apply(self, decision_result: dict[str, Any]) -> bool:
        return decision_result.get("decision") == ApplicationDecision.APPLY.value
