from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from agents.tracking_agent import TrackingAgent
from agents.workflow import JobApplicationOrchestrator
from config.settings import ApplicationStatus, load_config
from database.models import init_database
from database.repository import Repository

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["api"])

# ---------------------------------------------------------------------------
# Lazy-initialized globals (set in main.py via init_api)
# ---------------------------------------------------------------------------
_orchestrator: JobApplicationOrchestrator | None = None
_repo: Repository | None = None
_tracking: TrackingAgent | None = None


def init_api(orchestrator: JobApplicationOrchestrator, repo: Repository, tracking: TrackingAgent) -> None:
    global _orchestrator, _repo, _tracking
    _orchestrator = orchestrator
    _repo = repo
    _tracking = tracking


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------

class RunWorkflowResponse(BaseModel):
    status: str
    jobs_found: int
    applied: int
    skipped: int
    review: int
    report: dict[str, Any] = {}


class UpdateStatusRequest(BaseModel):
    status: str
    notes: str = ""


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "ai-job-agent"}


@router.post("/workflow/run", response_model=RunWorkflowResponse)
def run_workflow() -> RunWorkflowResponse:
    if not _orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")
    result = _orchestrator.run()
    return RunWorkflowResponse(
        status="completed",
        jobs_found=len(result.get("jobs", [])),
        applied=len(result.get("applied_jobs", [])),
        skipped=len(result.get("skipped_jobs", [])),
        review=len(result.get("review_jobs", [])),
        report=result.get("daily_report", {}),
    )


@router.get("/applications")
def list_applications(limit: int = 100) -> list[dict[str, Any]]:
    if not _repo:
        raise HTTPException(status_code=503, detail="Repository not initialized")
    return [a.to_dict() for a in _repo.get_all_applications(limit)]


@router.get("/applications/{job_id}")
def get_application(job_id: str) -> dict[str, Any]:
    if not _repo:
        raise HTTPException(status_code=503, detail="Repository not initialized")
    app = _repo.get_application_by_job_id(job_id)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    return app.to_dict()


@router.put("/applications/{job_id}/status")
def update_application_status(job_id: str, req: UpdateStatusRequest) -> dict[str, str]:
    if not _repo:
        raise HTTPException(status_code=503, detail="Repository not initialized")
    try:
        status = ApplicationStatus(req.status)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid status: {req.status}")
    _repo.update_application(job_id=job_id, status=status.value, notes=req.notes)
    return {"status": "updated", "job_id": job_id}


@router.get("/dashboard")
def dashboard_stats() -> dict[str, Any]:
    if not _repo:
        raise HTTPException(status_code=503, detail="Repository not initialized")
    return _repo.get_dashboard_stats()


@router.get("/dashboard/platforms")
def platform_breakdown() -> dict[str, int]:
    if not _repo:
        raise HTTPException(status_code=503, detail="Repository not initialized")
    return _repo.get_platform_breakdown()


@router.get("/dashboard/scores")
def score_distribution() -> dict[str, Any]:
    if not _repo:
        raise HTTPException(status_code=503, detail="Repository not initialized")
    return _repo.get_score_distribution()


@router.get("/reports")
def list_reports(days: int = 30) -> list[dict[str, Any]]:
    if not _repo:
        raise HTTPException(status_code=503, detail="Repository not initialized")
    reports = _repo.get_recent_reports(days)
    return [
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
        for r in reports
    ]


@router.post("/sheets/sync")
def sync_to_sheets() -> dict[str, str]:
    if not _tracking:
        raise HTTPException(status_code=503, detail="Tracking agent not initialized")
    _tracking.sync_to_sheets()
    return {"status": "synced"}


@router.post("/workflow/search")
def search_only() -> dict[str, Any]:
    if not _orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")
    jobs = _orchestrator.run_search_only()
    return {"jobs_found": len(jobs), "jobs": jobs}
