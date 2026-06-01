from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, AsyncGenerator, Optional

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import PromptBase
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import WordCompleter

from agents.application_agent import ApplicationAgent
from agents.cover_letter_agent import CoverLetterAgent
from agents.ranking_agent import RankingAgent
from agents.resume_agent import ResumeAgent
from agents.search_agent import SearchAgent
from agents.tracking_agent import TrackingAgent
from agents.workflow import JobApplicationOrchestrator
from config.settings import AppConfig
from database.repository import Repository
from services.groq_service import GroqService

logger = logging.getLogger(__name__)

# ── Plugin Context ────────────────────────────────────────────────────────────


@dataclass
class PluginContext:
    """Shared context passed to every plugin execution."""

    config: AppConfig
    repo: Repository
    groq: GroqService
    orchestrator: JobApplicationOrchestrator
    candidate_profile: str
    session_id: str
    console: Console
    memory: dict[str, Any] = field(default_factory=dict)

    # Internal state for conversation flow
    _state: dict[str, Any] = field(default_factory=dict)

    # Prompt session for interactive input
    _prompt_session: Optional[PromptSession] = None

    def get_prompt_session(self) -> PromptSession:
        if self._prompt_session is None:
            hist_path = Path("data") / f"history_{self.session_id}.txt"
            hist_path.parent.mkdir(parents=True, exist_ok=True)
            self._prompt_session = PromptSession(
                history=FileHistory(str(hist_path)),
                auto_suggest=AutoSuggestFromHistory(),
            )
        return self._prompt_session

    async def ask(self, prompt: str = "> ", password: bool = False) -> str:
        """Prompt the user for input during a plugin execution.

        This pauses the async generator and waits for user input
        via prompt_toolkit, then resumes.
        """
        session = self.get_prompt_session()
        return await session.prompt_async(prompt, is_password=password)

    def store(self, key: str, value: Any) -> None:
        self._state[key] = value

    def recall(self, key: str, default: Any = None) -> Any:
        return self._state.get(key, default)

    def clear_state(self) -> None:
        self._state.clear()


# ── Plugin Protocol ───────────────────────────────────────────────────────────


class Plugin:
    """Base class for all slash-command plugins."""

    name: str = ""
    description: str = ""
    aliases: list[str] = field(default_factory=list)

    async def execute(
        self, args: str, context: PluginContext
    ) -> AsyncGenerator[str, None]:
        """Execute the plugin command.

        Args:
            args: The arguments following the slash command (trimmed).
            context: Shared plugin context.

        Yields:
            Strings to be rendered with typing animation.
            May call ``context.ask()`` to get interactive user input.
        """
        # Override in subclass
        yield f"Plugin {self.name} executed with args: {args}"

    def matches(self, command: str) -> bool:
        """Check if this plugin handles the given command."""
        cmd = command.lower().strip()
        if cmd == self.name.lower():
            return True
        for alias in self.aliases:
            if cmd == alias.lower():
                return True
        return False


# ── Plugin Registry ───────────────────────────────────────────────────────────


class PluginRegistry:
    """Registry of all available slash-command plugins."""

    def __init__(self) -> None:
        self._plugins: dict[str, Plugin] = {}

    def register(self, plugin: Plugin) -> None:
        """Register a plugin by its name and aliases."""
        self._plugins[plugin.name.lower()] = plugin
        for alias in plugin.aliases:
            self._plugins[alias.lower()] = plugin
        logger.info("Registered plugin: %s (aliases: %s)", plugin.name, plugin.aliases)

    def get(self, command: str) -> Optional[Plugin]:
        """Get a plugin matching the given command string."""
        key = command.lower().strip()
        return self._plugins.get(key)

    def resolve(self, input_str: str) -> tuple[Optional[Plugin], str]:
        """Resolve a full input line to (plugin, args).

        If input is /command rest_of_line, split and match.
        Returns (None, input_str) if no plugin matches.
        """
        input_str = input_str.strip()
        if not input_str.startswith("/"):
            return None, input_str

        parts = input_str.split(maxsplit=1)
        command = parts[0].lstrip("/")
        args = parts[1] if len(parts) > 1 else ""

        plugin = self.get(command)
        return plugin, args

    def all_plugins(self) -> list[Plugin]:
        seen: set[str] = set()
        result: list[Plugin] = []
        for p in self._plugins.values():
            if p.name not in seen:
                seen.add(p.name)
                result.append(p)
        return result

    def commands_list(self) -> list[tuple[str, str, str]]:
        """Return (name, aliases_str, description) for all registered plugins."""
        seen: dict[str, Plugin] = {}
        for p in self._plugins.values():
            seen[p.name] = p
        result = []
        for name, plugin in seen.items():
            aliases_str = ", ".join(
                f"/{a}" for a in plugin.aliases if a != name
            )
            result.append((f"/{name}", aliases_str, plugin.description))
        return result
