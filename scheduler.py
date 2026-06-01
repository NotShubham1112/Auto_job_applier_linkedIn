from __future__ import annotations

import logging
import time
from datetime import datetime, timedelta

from agents.workflow import JobApplicationOrchestrator
from config.settings import AppConfig
from database.repository import Repository

logger = logging.getLogger(__name__)


def run_scheduler(config: AppConfig, repo: Repository, profile: str) -> None:
    """Run the daily automated workflow on a schedule."""
    if not config.scheduler.enabled:
        logger.info("Scheduler is disabled. Use --mode run for single execution.")
        return

    logger.info("Scheduler started. Waiting for scheduled times...")

    def _parse_time(time_str: str) -> tuple[int, int]:
        parts = time_str.split(":")
        return int(parts[0]), int(parts[1])

    search_h, search_m = _parse_time(config.scheduler.search_time)
    rank_h, rank_m = _parse_time(config.scheduler.rank_time)
    generate_h, generate_m = _parse_time(config.scheduler.generate_time)
    apply_h, apply_m = _parse_time(config.scheduler.apply_time)
    report_h, report_m = _parse_time(config.scheduler.report_time)

    executed_today: set[str] = set()

    while True:
        now = datetime.now()
        today = now.date().isoformat()

        # Reset executed tasks at midnight
        if now.hour == 0 and now.minute == 0:
            executed_today.clear()

        # Search
        key = f"search_{today}"
        if now.hour == search_h and now.minute == search_m and key not in executed_today:
            logger.info("SCHEDULED: Running job search...")
            orchestrator = JobApplicationOrchestrator(config, repo, profile)
            try:
                orchestrator.run()
            except Exception as e:
                logger.error("Scheduled search failed: %s", e)
            finally:
                orchestrator.close()
            executed_today.add(key)

        # Sleep 60 seconds between checks
        time.sleep(60)


def run_daily_workflow(config: AppConfig, repo: Repository, profile: str) -> dict:
    """Execute the full daily workflow and return results."""
    orchestrator = JobApplicationOrchestrator(config, repo, profile)
    try:
        result = orchestrator.run()
        return {
            "status": "completed",
            "jobs_found": len(result.get("jobs", [])),
            "applied": len(result.get("applied_jobs", [])),
            "skipped": len(result.get("skipped_jobs", [])),
            "review": len(result.get("review_jobs", [])),
            "report": result.get("daily_report", {}),
        }
    finally:
        orchestrator.close()
