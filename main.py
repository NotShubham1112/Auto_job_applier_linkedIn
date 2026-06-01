from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

import uvicorn

# Ensure project root is on sys.path
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agents.tracking_agent import TrackingAgent
from agents.workflow import JobApplicationOrchestrator
from api.routes import init_api, router as api_router
from config.settings import load_config
from database.models import init_database
from database.repository import Repository
from services.google_sheets_service import GoogleSheetsService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
    ],
)
# Also log to file if logs dir exists
Path("logs").mkdir(exist_ok=True)
file_handler = logging.FileHandler("logs/agent.log", encoding="utf-8")
file_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
logging.getLogger().addHandler(file_handler)
logger = logging.getLogger("job_agent")


def load_candidate_profile(path: str = "shubham.md") -> str:
    p = Path(path)
    if p.exists():
        return p.read_text(encoding="utf-8")
    logger.warning("Candidate profile not found at %s", path)
    return ""


def main() -> None:
    parser = argparse.ArgumentParser(description="AI Job Application Agent")
    parser.add_argument("--mode", choices=["run", "api", "search", "rank", "scheduler", "chat"], default="chat")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--profile", default="shubham.md")
    args = parser.parse_args()

    # Load config
    config = load_config()

    # Init database
    Path("data").mkdir(exist_ok=True)
    session_factory = init_database(config.database)
    session = session_factory()
    repo = Repository(session)

    # Load candidate profile
    profile = load_candidate_profile(args.profile)

    # Create orchestrator
    orchestrator = JobApplicationOrchestrator(config, repo, profile)

    if args.mode == "api":
        # FastAPI server
        from fastapi import FastAPI
        from fastapi.middleware.cors import CORSMiddleware

        app = FastAPI(title="AI Job Application Agent", version="1.0.0")
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        app.include_router(api_router)

        tracking = TrackingAgent(config, repo)
        init_api(orchestrator, repo, tracking)

        logger.info("Starting API server on %s:%d", args.host, args.port)
        uvicorn.run(app, host=args.host, port=args.port)

    elif args.mode == "run":
        # Single full workflow run
        logger.info("Starting full workflow run...")
        result = orchestrator.run()
        logger.info("Workflow complete. Applied: %d, Skipped: %d, Review: %d",
                     len(result.get("applied_jobs", [])),
                     len(result.get("skipped_jobs", [])),
                     len(result.get("review_jobs", [])))

    elif args.mode == "search":
        logger.info("Running search only...")
        jobs = orchestrator.run_search_only()
        logger.info("Found %d jobs", len(jobs))
        for j in jobs[:10]:
            logger.info("  - %s at %s (%s)", j.get("title"), j.get("company"), j.get("platform"))

    elif args.mode == "rank":
        logger.info("Running search + rank...")
        jobs = orchestrator.run_search_only()
        ranked = orchestrator.run_rank_only(jobs)
        ranked.sort(key=lambda x: x[1].get("score", 0), reverse=True)
        logger.info("Ranked %d jobs:", len(ranked))
        for j, r in ranked[:10]:
            logger.info("  [%.0f] %s at %s", r.get("score", 0), j.get("title"), j.get("company"))

    elif args.mode == "scheduler":
        from scheduler import run_scheduler
        run_scheduler(config, repo, profile)

    elif args.mode == "chat":
        from cli.app import InteractiveCLI

        app = InteractiveCLI(config)
        app.initialize()
        app.run()
        return

    # Cleanup
    orchestrator.close()
    session.close()


if __name__ == "__main__":
    main()
