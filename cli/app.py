from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import Any, Optional

from rich.console import Console

from agents.tracking_agent import TrackingAgent
from agents.workflow import JobApplicationOrchestrator
from chat.engine import ChatEngine
from chat.memory import ConversationMemory
from chat.router import CommandRouter
from chat.session import SessionManager
from config.settings import AppConfig, load_config
from database.models import init_database
from database.repository import Repository
from services.google_sheets_service import GoogleSheetsService
from services.groq_service import GroqService

# ── Plugins ──
from plugins.agent_plugin import AgentPlugin
from plugins.apply_plugin import ApplyPlugin
from plugins.chat_plugin import ChatPlugin
from plugins.clear_plugin import ClearPlugin
from plugins.coverletter_plugin import CoverLetterPlugin
from plugins.exit_plugin import ExitPlugin
from plugins.help_plugin import HelpPlugin
from plugins.history_plugin import HistoryPlugin
from plugins.interviews_plugin import InterviewsPlugin
from plugins.jobs_plugin import JobsPlugin
from plugins.jobhunt_plugin import JobHuntPlugin
from plugins.resume_plugin import ResumePlugin
from plugins.search_plugin import SearchPlugin
from plugins.settings_plugin import SettingsPlugin
from plugins.status_plugin import StatusPlugin

logger = logging.getLogger(__name__)


class InteractiveCLI:
    """Main interactive CLI application.

    Initializes all services, agents, memory, and plugins,
    then starts the chat engine.
    """

    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self.console = Console()
        self._services_initialized = False

    def initialize(self) -> None:
        """Initialize database, agents, services, and plugins."""
        logger.info("Initializing InteractiveCLI...")

        # ── UTF-8 output for Windows ──
        import sys
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8')

        # ── Database ──
        Path("data").mkdir(exist_ok=True)
        session_factory = init_database(self.config.database)
        self._db_session = session_factory()
        self.repo = Repository(self._db_session)

        # ── Candidate Profile ──
        self.candidate_profile = self._load_candidate_profile()

        # ── Services ──
        self.groq = GroqService(self.config.ai)
        self.sheets = GoogleSheetsService(self.config.google_sheets)
        if self.config.google_sheets.enabled:
            try:
                self.sheets.connect()
            except Exception as e:
                logger.warning("Google Sheets connection failed: %s", e)

        # ── Orchestrator (reuse services to avoid duplicate init) ──
        self.orchestrator = JobApplicationOrchestrator(
            self.config, self.repo, self.candidate_profile,
            groq=self.groq, sheets=self.sheets,
        )

        # ── Session & Memory ──
        self.session_manager = SessionManager()
        self.memory = ConversationMemory(self.session_manager)
        self.memory.init_session()

        # ── Router ──
        self.router = CommandRouter(
            config=self.config,
            repo=self.repo,
            groq=self.groq,
            orchestrator=self.orchestrator,
            candidate_profile=self.candidate_profile,
            memory=self.memory,
            console=self.console,
        )

        # ── Register Plugins ──
        self._register_plugins()

        self._services_initialized = True
        logger.info("InteractiveCLI initialized (session: %s)", self.memory.session_id)

    def _register_plugins(self) -> None:
        """Register all slash-command plugins."""
        plugins = [
            HelpPlugin(),
            JobHuntPlugin(),
            SearchPlugin(),
            ApplyPlugin(),
            StatusPlugin(),
            JobsPlugin(),
            InterviewsPlugin(),
            ResumePlugin(),
            CoverLetterPlugin(),
            SettingsPlugin(),
            HistoryPlugin(),
            ClearPlugin(),
            ExitPlugin(),
            ChatPlugin(),
            AgentPlugin(),
        ]
        for plugin in plugins:
            self.router.register(plugin)

    async def run_async(self) -> None:
        """Start the interactive chat loop."""
        if not self._services_initialized:
            self.initialize()

        engine = ChatEngine(self.router, self.memory, self.config)
        try:
            await engine.run()
        except KeyboardInterrupt:
            logger.info("User interrupted")
        finally:
            self._cleanup()

    def run(self) -> None:
        """Synchronous entry point — creates event loop and runs."""
        asyncio.run(self.run_async())

    def _cleanup(self) -> None:
        """Clean up resources."""
        try:
            self.orchestrator.close()
        except Exception:
            pass
        try:
            self._db_session.close()
        except Exception:
            pass
        self.console.print()
        self.console.print("[dim]Session ended. Resources cleaned up.[/dim]")

    def _load_candidate_profile(self, path: str = "shubham.md") -> str:
        p = Path(path)
        if p.exists():
            return p.read_text(encoding="utf-8")
        logger.warning("Candidate profile not found at %s", path)
        return ""
