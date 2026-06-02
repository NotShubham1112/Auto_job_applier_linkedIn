"""CLI entrypoint — launches the BROWORK Textual app.

This module is the glue between ``main.py`` and the new Textual-based
BROWORK experience. The legacy Rich/prompt_toolkit-based chat engine
in ``chat/engine.py`` is still available as a fallback, but the new
Textual app is the default.
"""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import Any, Optional

from config.settings import AppConfig, load_config
from database.models import init_database
from database.repository import Repository

logger = logging.getLogger(__name__)


class InteractiveCLI:
    """Main interactive CLI application.

    The new Textual implementation replaces the older
    prompt_toolkit-based chat engine. The interface is the same as
    before so callers (e.g. ``main.py``) don't need to change.
    """

    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self._services_initialized = False
        self._app: Optional[Any] = None
        self._repo: Optional[Repository] = None
        self._db_session: Any = None

    def initialize(self) -> None:
        """Initialize database and other services that don't need the app."""
        import sys
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")

        Path("data").mkdir(exist_ok=True)
        session_factory = init_database(self.config.database)
        self._db_session = session_factory()
        self._repo = Repository(self._db_session)
        self._services_initialized = True
        logger.info("InteractiveCLI services initialized")

    async def run_async(self) -> None:
        """Start the Textual app."""
        if not self._services_initialized:
            self.initialize()

        from cli.textual_app import build_app

        self._app = build_app(config=self.config)
        if self._repo is not None:
            self._app.repo = self._repo

        try:
            await self._app.run_async()
        except KeyboardInterrupt:
            logger.info("User interrupted")
        finally:
            self._cleanup()

    def run(self) -> None:
        """Synchronous entry point — runs the Textual app."""
        try:
            self.run_sync()
        except KeyboardInterrupt:
            pass

    def run_sync(self) -> None:
        """Synchronous entry point that bridges from a sync context."""
        asyncio.run(self.run_async())

    def _cleanup(self) -> None:
        """Clean up resources."""
        try:
            if self._app is not None and getattr(self._app, "orchestrator", None):
                self._app.orchestrator.close()
        except Exception:
            pass
        try:
            if self._db_session is not None:
                self._db_session.close()
        except Exception:
            pass

    def _load_candidate_profile(self, path: str = "shubham.md") -> str:
        p = Path(path)
        if p.exists():
            return p.read_text(encoding="utf-8")
        logger.warning("Candidate profile not found at %s", path)
        return ""
