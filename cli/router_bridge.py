"""Bridge between the existing plugin/router system and the Textual app.

The Textual app owns the UI, but the actual command dispatch and LLM
streaming happen in the existing ``CommandRouter`` / ``Plugin`` code.
This module builds a ``PluginContext`` that the router can use, then
runs the router's async generator in a Textual worker, streaming each
token into the UI as it arrives.
"""

from __future__ import annotations

import asyncio
import datetime as dt
import logging
from typing import Any, AsyncGenerator, Optional

from rich.console import Console
from rich.text import Text

from chat.memory import ConversationMemory
from chat.router import CommandRouter
from config.settings import AppConfig
from database.repository import Repository
from plugins.agent_plugin import AgentPlugin
from plugins.apply_plugin import ApplyPlugin
from plugins.base import Plugin, PluginContext, PluginRegistry
from plugins.chat_plugin import ChatPlugin
from plugins.clear_plugin import ClearPlugin
from plugins.coverletter_plugin import CoverLetterPlugin
from plugins.developer_plugins import (
    ArchitectPlugin,
    BuildPlugin,
    DebugPlugin,
    FixPlugin,
    ResearchPlugin,
    ReviewPlugin,
    ShipPlugin,
)
from plugins.exit_plugin import ExitPlugin
from plugins.help_plugin import HelpPlugin
from plugins.history_plugin import HistoryPlugin
from plugins.interviews_plugin import InterviewsPlugin
from plugins.jobhunt_plugin import JobHuntPlugin
from plugins.jobs_plugin import JobsPlugin
from plugins.resume_plugin import ResumePlugin
from plugins.search_plugin import SearchPlugin
from plugins.settings_plugin import SettingsPlugin
from plugins.status_plugin import StatusPlugin
from services.groq_service import GroqService

logger = logging.getLogger(__name__)


# ── Plugin list ────────────────────────────────────────────────────────────

def _build_plugins() -> list[Plugin]:
    """Return the list of every plugin the CLI should register.

    This is the OpenCode-style list — job-hunt plugins + the new
    developer-focused ones (/research, /build, /fix, /review,
    /architect, /debug, /ship).
    """
    return [
        # Core
        HelpPlugin(),
        ExitPlugin(),
        ClearPlugin(),
        HistoryPlugin(),
        SettingsPlugin(),
        # Job hunting
        JobHuntPlugin(),
        SearchPlugin(),
        StatusPlugin(),
        JobsPlugin(),
        ApplyPlugin(),
        InterviewsPlugin(),
        # Resume & docs
        ResumePlugin(),
        CoverLetterPlugin(),
        ChatPlugin(),
        # Agent mode
        AgentPlugin(),
        # Developer-focused (OpenCode style)
        ResearchPlugin(),
        BuildPlugin(),
        FixPlugin(),
        ReviewPlugin(),
        ArchitectPlugin(),
        DebugPlugin(),
        ShipPlugin(),
    ]


# ── Router factory ────────────────────────────────────────────────────────


def build_router(
    config: AppConfig,
    repo: Repository,
    groq: GroqService,
    orchestrator: Any,
    candidate_profile: str,
    memory: ConversationMemory,
) -> tuple[CommandRouter, PluginRegistry]:
    """Build a CommandRouter pre-loaded with every plugin."""
    router = CommandRouter(
        config=config,
        repo=repo,
        groq=groq,
        orchestrator=orchestrator,
        candidate_profile=candidate_profile,
        memory=memory,
        console=Console(),  # unused for Textual rendering
    )
    for plugin in _build_plugins():
        router.register(plugin)
    return router, router.registry


# ── Streaming helper ──────────────────────────────────────────────────────


async def stream_router_to_app(
    router: CommandRouter,
    user_input: str,
    *,
    on_token: Any,
    on_status: Any,
    on_finish: Any,
) -> None:
    """Run the router on ``user_input`` and stream tokens via callbacks.

    Args:
        router: The CommandRouter to dispatch through.
        user_input: The raw user input string.
        on_token: Callable(token_str) -> awaitable or None.
        on_status: Callable(message_str) -> awaitable or None.
        on_finish: Callable(full_response) -> awaitable or None.

    The function rotates a few loading messages while the first token
    hasn't arrived yet, then streams the actual response.
    """
    full_response = ""
    first_token = True
    status_task: Optional[asyncio.Task] = None
    stop_event = asyncio.Event()

    async def _status_rotator():
        from cli.loading import rotating_messages
        msg_iter = rotating_messages(interval=700, seed=None)
        i = 0
        while not stop_event.is_set():
            try:
                msg = next(msg_iter)
            except StopIteration:
                msg = "Working..."
            if on_status is not None:
                try:
                    res = on_status(msg)
                    if asyncio.iscoroutine(res):
                        await res
                except Exception:
                    pass
            await asyncio.sleep(0.7)
            i += 1

    try:
        async for token in router.route(user_input):
            if first_token:
                first_token = False
                stop_event.set()
                if status_task is not None:
                    status_task.cancel()
                    try:
                        await status_task
                    except (asyncio.CancelledError, Exception):
                        pass
                if on_status is not None:
                    try:
                        res = on_status("")
                        if asyncio.iscoroutine(res):
                            await res
                    except Exception:
                        pass

            full_response += token
            if on_token is not None:
                try:
                    res = on_token(token)
                    if asyncio.iscoroutine(res):
                        await res
                except Exception:
                    pass

        # If the response was empty, ensure the rotator still stops
        if first_token:
            stop_event.set()
            if status_task is not None:
                status_task.cancel()
                try:
                    await status_task
                except (asyncio.CancelledError, Exception):
                    pass
    except SystemExit:
        stop_event.set()
        if status_task is not None:
            status_task.cancel()
        raise
    except Exception as e:
        stop_event.set()
        if status_task is not None:
            status_task.cancel()
        logger.exception("Router failed")
        if on_token is not None:
            try:
                res = on_token(f"\n\n**Error:** {e}\n")
                if asyncio.iscoroutine(res):
                    await res
            except Exception:
                pass
    finally:
        stop_event.set()
        if status_task is not None:
            try:
                status_task.cancel()
                await status_task
            except (asyncio.CancelledError, Exception):
                pass

    if on_finish is not None:
        try:
            res = on_finish(full_response)
            if asyncio.iscoroutine(res):
                await res
        except Exception:
            pass
