"""BROWORK main Textual App.

The App ties everything together:
  - Initializes services (config, DB, LLM, plugins)
  - Shows the BootScreen on launch
  - After boot, swaps in the MainScreen
  - Exposes a global command palette (ctrl+x) and quit (ctrl+c)
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Optional

from textual.app import App
from textual.binding import Binding

from chat.memory import ConversationMemory
from chat.session import SessionManager
from cli.router_bridge import build_router
from cli.screens.boot_screen import BootScreen
from cli.screens.main_screen import MainScreen
from cli.styles.css import get_css
from config.settings import AppConfig, load_config
from database.models import init_database
from database.repository import Repository
from services.google_sheets_service import GoogleSheetsService
from services.groq_service import GroqService

logger = logging.getLogger(__name__)


class BroworkApp(App[None]):
    """The top-level BROWORK Textual application."""

    TITLE = "BROWORK"
    SUB_TITLE = "AI Engineering Workspace"

    BINDINGS = [
        Binding("ctrl+c", "quit_app", "Quit", show=False, priority=True),
    ]

    CSS = get_css()

    def __init__(
        self,
        config: AppConfig,
        repo: Repository,
        groq: GroqService,
        candidate_profile: str,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.config = config
        self.repo = repo
        self.groq = groq
        self.candidate_profile = candidate_profile

        # Will be filled in once services are ready
        self.orchestrator = None
        self.memory: Optional[ConversationMemory] = None
        self.router = None
        self.registry = None

    # ── Textual lifecycle ────────────────────────────────────────────

    def on_mount(self) -> None:
        # Start the boot screen
        self.push_screen(BootScreen())

    async def on_unmount(self) -> None:
        # Cleanup: close DB session, etc.
        try:
            if self.orchestrator is not None:
                self.orchestrator.close()
        except Exception:
            pass

    # ── Watcher for boot → main transition ───────────────────────────

    def on_screen_resume(self) -> None:
        # No-op; the BootScreen pops itself when done
        pass

    # ── Action exposed to the app ────────────────────────────────────

    def action_quit_app(self) -> None:
        self.exit()

    # ── Public hook used by BootScreen ───────────────────────────────

    def transition_to_main(self) -> None:
        """Called by the BootScreen (or anywhere) to swap in MainScreen."""
        if self.memory is None or self.router is None or self.registry is None:
            self._initialize_services()
        self.push_screen(MainScreen(
            config=self.config,
            router=self.router,
            registry=self.registry,
            memory=self.memory,
        ))

    # ── Service init ─────────────────────────────────────────────────

    def _initialize_services(self) -> None:
        """Initialize the orchestrator / memory / router on demand.

        This is called by ``transition_to_main`` so that the boot
        screen is shown first, *then* the (slower) service init runs.
        """
        # Session & memory
        Path("data").mkdir(exist_ok=True)
        session_manager = SessionManager()
        self.memory = ConversationMemory(session_manager)
        self.memory.init_session()

        # Orchestrator
        from agents.workflow import JobApplicationOrchestrator
        try:
            sheets = GoogleSheetsService(self.config.google_sheets)
            if self.config.google_sheets.enabled:
                try:
                    sheets.connect()
                except Exception as e:
                    logger.warning("Google Sheets connection failed: %s", e)
        except Exception:
            sheets = None
        try:
            self.orchestrator = JobApplicationOrchestrator(
                self.config, self.repo, self.candidate_profile,
                groq=self.groq, sheets=sheets,
            )
        except Exception as e:
            logger.warning("Orchestrator init failed: %s", e)
            self.orchestrator = None

        # Router
        self.router, self.registry = build_router(
            config=self.config,
            repo=self.repo,
            groq=self.groq,
            orchestrator=self.orchestrator,
            candidate_profile=self.candidate_profile,
            memory=self.memory,
        )
        logger.info("BROWORK services initialized")


# ── Factory ────────────────────────────────────────────────────────────


def build_app(
    config: Optional[AppConfig] = None,
    skip_db: bool = False,
) -> BroworkApp:
    """Build a fully-initialized BroworkApp.

    The function handles:
      - UTF-8 reconfigure on Windows
      - Config loading
      - DB init (skippable for headless tests)
      - Groq service init
      - Loading the candidate profile
    """
    # UTF-8 on Windows
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
    if hasattr(sys.stderr, "reconfigure"):
        try:
            sys.stderr.reconfigure(encoding="utf-8")
        except Exception:
            pass

    # Config
    if config is None:
        config = load_config()

    # DB + repo
    repo: Optional[Repository] = None
    if not skip_db:
        Path("data").mkdir(exist_ok=True)
        session_factory = init_database(config.database)
        session = session_factory()
        repo = Repository(session)
    else:
        # Build a dummy repo that will not be used
        repo = None  # type: ignore

    # Groq
    groq = GroqService(config.ai)

    # Candidate profile
    profile_path = Path("shubham.md")
    if profile_path.exists():
        profile = profile_path.read_text(encoding="utf-8")
    else:
        profile = ""

    app = BroworkApp(
        config=config,
        repo=repo,
        groq=groq,
        candidate_profile=profile,
    )
    # Initialize services up-front so MainScreen can be pushed
    # immediately after the boot screen pops.
    app._initialize_services()
    return app
