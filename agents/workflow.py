from __future__ import annotations

import json
import logging
import time
from typing import Any, TypedDict

from langgraph.graph import END, StateGraph

from agents.application_agent import ApplicationAgent
from agents.cover_letter_agent import CoverLetterAgent
from agents.ranking_agent import RankingAgent
from agents.resume_agent import ResumeAgent
from agents.search_agent import SearchAgent
from agents.tracking_agent import TrackingAgent
from config.settings import AppConfig, ApplicationDecision, ApplicationStatus
from database.repository import Repository
from services.groq_service import GroqService
from services.google_sheets_service import GoogleSheetsService

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Workflow state
# ---------------------------------------------------------------------------

class AgentState(TypedDict, total=False):
    jobs: list[dict[str, Any]]
    enriched_jobs: list[dict[str, Any]]
    ranked_jobs: list[tuple[dict[str, Any], dict[str, Any]]]
    applied_jobs: list[dict[str, Any]]
    skipped_jobs: list[dict[str, Any]]
    review_jobs: list[dict[str, Any]]
    daily_report: dict[str, Any]
    candidate_profile: str
    error: str


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------

class JobApplicationOrchestrator:
    """LangGraph-based workflow orchestrator for the AI Job Application Agent."""

    def __init__(
        self,
        config: AppConfig,
        repo: Repository,
        candidate_profile: str = "",
        groq: GroqService | None = None,
        sheets: GoogleSheetsService | None = None,
    ) -> None:
        self.config = config
        self.repo = repo

        # Initialize services (reuse if provided)
        self.groq = groq or GroqService(config.ai)
        self.sheets = sheets or GoogleSheetsService(config.google_sheets)
        if config.google_sheets.enabled and not sheets:
            self.sheets.connect()

        # Initialize agents
        self.search_agent = SearchAgent(config, repo)
        self.ranking_agent = RankingAgent(config, repo, self.groq)
        self.resume_agent = ResumeAgent(config, repo, self.groq)
        self.cover_letter_agent = CoverLetterAgent(config, repo, self.groq)
        self.application_agent = ApplicationAgent(config, repo, self.groq)
        self.tracking_agent = TrackingAgent(config, repo, self.sheets)

        # Set candidate profile on agents
        self._candidate_profile = candidate_profile
        self.resume_agent.set_candidate_profile(candidate_profile)
        self.cover_letter_agent.set_candidate_profile(candidate_profile)
        self.application_agent.set_candidate_profile(candidate_profile)

        # Build the graph
        self._graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        graph = StateGraph(AgentState)

        # Add nodes
        graph.add_node("search", self._search_node)
        graph.add_node("enrich", self._enrich_node)
        graph.add_node("rank", self._rank_node)
        graph.add_node("decide", self._decide_node)
        graph.add_node("generate_documents", self._generate_documents_node)
        graph.add_node("apply", self._apply_node)
        graph.add_node("track", self._track_node)
        graph.add_node("report", self._report_node)

        # Set entry point
        graph.set_entry_point("search")

        # Edges
        graph.add_edge("search", "enrich")
        graph.add_edge("enrich", "rank")
        graph.add_edge("rank", "decide")
        graph.add_conditional_edges("decide", self._route_after_decide, {
            "generate": "generate_documents",
            "skip": "track",
            "report": "report",
        })
        graph.add_edge("generate_documents", "apply")
        graph.add_edge("apply", "track")
        graph.add_edge("track", "report")
        graph.add_edge("report", END)

        return graph.compile()

    # ------------------------------------------------------------------
    # Node implementations
    # ------------------------------------------------------------------

    def _search_node(self, state: AgentState) -> dict:
        logger.info("=== SEARCH NODE ===")
        try:
            jobs = self.search_agent.search()
            return {"jobs": jobs, "error": ""}
        except Exception as e:
            logger.error("Search failed: %s", e)
            return {"jobs": [], "error": str(e)}

    def _enrich_node(self, state: AgentState) -> dict:
        logger.info("=== ENRICH NODE ===")
        jobs = state.get("jobs", [])
        enriched = []
        for job in jobs:
            try:
                enriched_job = self.search_agent.enrich_job(job)
                enriched.append(enriched_job)
            except Exception as e:
                logger.warning("Failed to enrich job %s: %s", job.get("job_id"), e)
                enriched.append(job)
        return {"enriched_jobs": enriched}

    def _rank_node(self, state: AgentState) -> dict:
        logger.info("=== RANK NODE ===")
        jobs = state.get("enriched_jobs", [])
        profile = state.get("candidate_profile", self._candidate_profile)

        # Quick rule-based pre-rank to pick top candidates before calling AI
        quick_ranked = []
        for job in jobs:
            try:
                ranking = self.ranking_agent.rank(job, profile)
                quick_ranked.append((job, ranking))
            except Exception as e:
                logger.warning("Failed to rank job %s: %s", job.get("job_id"), e)

        # Sort by score, take top N for expensive AI decision step
        quick_ranked.sort(key=lambda x: x[1].get("score", 0), reverse=True)
        max_ai_jobs = 20
        ranked = quick_ranked[:max_ai_jobs]
        skipped_rest = quick_ranked[max_ai_jobs:]

        logger.info("Ranked %d jobs total, top %d sent to AI decision", len(quick_ranked), len(ranked))
        return {"ranked_jobs": ranked}

    def _decide_node(self, state: AgentState) -> dict:
        logger.info("=== DECIDE NODE ===")
        ranked = state.get("ranked_jobs", [])
        profile = state.get("candidate_profile", self._candidate_profile)
        applied = []
        skipped = []
        review = []

        for job, ranking in ranked:
            try:
                decision = self.application_agent.decide(job, ranking)
                if decision["decision"] == ApplicationDecision.APPLY.value:
                    applied.append({"job": job, "ranking": ranking, "decision": decision})
                elif decision["decision"] == ApplicationDecision.REVIEW.value:
                    review.append({"job": job, "ranking": ranking, "decision": decision})
                else:
                    skipped.append({"job": job, "ranking": ranking, "decision": decision})
            except Exception as e:
                logger.warning("Decision failed for %s: %s", job.get("job_id"), e)
                skipped.append({"job": job, "ranking": ranking, "decision": {"decision": "SKIP", "confidence": 0, "reasoning": str(e)}})

        return {
            "applied_jobs": applied,
            "skipped_jobs": skipped,
            "review_jobs": review,
        }

    def _route_after_decide(self, state: AgentState) -> str:
        applied = state.get("applied_jobs", [])
        if applied:
            return "generate"
        return "report"

    def _generate_documents_node(self, state: AgentState) -> dict:
        logger.info("=== GENERATE DOCUMENTS NODE ===")
        applied = state.get("applied_jobs", [])
        for item in applied:
            job = item["job"]
            try:
                resume_path = self.resume_agent.select_best_resume(job)
                summary = self.resume_agent.tailor_summary(job)
                cover_letter = self.cover_letter_agent.generate(job)
                cl_path = self.cover_letter_agent.save(job, cover_letter)
                item["resume_path"] = resume_path
                item["cover_letter_path"] = cl_path
                item["tailored_summary"] = summary
            except Exception as e:
                logger.warning("Document generation failed for %s: %s", job.get("job_id"), e)
                item["resume_path"] = self.config.resume.default_resume_path
                item["cover_letter_path"] = ""
                item["tailored_summary"] = ""
        return {"applied_jobs": applied}

    def _apply_node(self, state: AgentState) -> dict:
        logger.info("=== APPLY NODE ===")
        applied = state.get("applied_jobs", [])
        for item in applied:
            job = item["job"]
            try:
                # Record in tracking
                self.tracking_agent.record_application(
                    job=job,
                    ranking=item["ranking"],
                    decision=item["decision"],
                    resume_path=item.get("resume_path", ""),
                    cover_letter_path=item.get("cover_letter_path", ""),
                )
                logger.info(
                    "APPLIED: %s at %s (score: %.1f, confidence: %.2f)",
                    job.get("title"),
                    job.get("company"),
                    item["ranking"].get("score", 0),
                    item["decision"].get("confidence", 0),
                )
            except Exception as e:
                logger.error("Application recording failed for %s: %s", job.get("job_id"), e)
        return {}

    def _track_node(self, state: AgentState) -> dict:
        logger.info("=== TRACK NODE ===")
        skipped = state.get("skipped_jobs", [])
        for item in skipped:
            job = item["job"]
            try:
                self.tracking_agent.record_application(
                    job=job,
                    ranking=item["ranking"],
                    decision=item["decision"],
                )
            except Exception as e:
                logger.warning("Tracking skip failed: %s", e)

        # Sync to Google Sheets if enabled
        self.tracking_agent.sync_to_sheets()
        return {}

    def _report_node(self, state: AgentState) -> dict:
        logger.info("=== REPORT NODE ===")
        try:
            report = self.tracking_agent.generate_daily_report()
            return {"daily_report": report}
        except Exception as e:
            logger.error("Report generation failed: %s", e)
            return {"daily_report": {}}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run(self) -> dict[str, Any]:
        """Execute the full workflow. Returns the final state."""
        initial_state: AgentState = {
            "jobs": [],
            "enriched_jobs": [],
            "ranked_jobs": [],
            "applied_jobs": [],
            "skipped_jobs": [],
            "review_jobs": [],
            "daily_report": {},
            "candidate_profile": self._candidate_profile,
            "error": "",
        }
        final_state = self._graph.invoke(initial_state)

        # Summary
        logger.info("=" * 60)
        logger.info("WORKFLOW COMPLETE")
        logger.info("Jobs found: %d", len(final_state.get("jobs", [])))
        logger.info("Jobs enriched: %d", len(final_state.get("enriched_jobs", [])))
        logger.info("Jobs ranked: %d", len(final_state.get("ranked_jobs", [])))
        logger.info("Applied: %d", len(final_state.get("applied_jobs", [])))
        logger.info("Skipped: %d", len(final_state.get("skipped_jobs", [])))
        logger.info("Review: %d", len(final_state.get("review_jobs", [])))
        logger.info("=" * 60)

        # Cleanup browser sessions
        self.search_agent.cleanup()

        return final_state

    def run_search_only(self) -> list[dict[str, Any]]:
        """Run only the search phase."""
        jobs = self.search_agent.search()
        enriched = [self.search_agent.enrich_job(j) for j in jobs]
        self.search_agent.cleanup()
        return enriched

    def run_rank_only(self, jobs: list[dict[str, Any]]) -> list[tuple[dict, dict]]:
        """Run only the ranking phase."""
        profile = self._candidate_profile
        return [(j, self.ranking_agent.rank(j, profile)) for j in jobs]

    def close(self) -> None:
        self.search_agent.cleanup()
        self.groq.close()
