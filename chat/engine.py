from __future__ import annotations

import asyncio
import logging
import sys
from typing import Any, AsyncGenerator, Optional

from prompt_toolkit import PromptSession
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.history import FileHistory
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.live import Live

from chat.memory import ConversationMemory
from chat.router import CommandRouter
from chat.session import SessionManager
from config.settings import AppConfig
from ui.components import (
    agent_panel,
    blank,
    console,
    divider,
    header,
    rule,
    stream_generator,
    stream_text,
)
from ui.styles import Palette

logger = logging.getLogger(__name__)


class ChatEngine:
    """Core chat engine — manages the interactive loop, streaming, and rendering.

    Integrates the command router, memory, and session management
    with a prompt_toolkit-driven REPL loop.
    """

    def __init__(
        self,
        router: CommandRouter,
        memory: ConversationMemory,
        config: AppConfig,
    ) -> None:
        self.router = router
        self.memory = memory
        self.config = config
        self._running = False

    async def run(self) -> None:
        """Main chat loop."""
        self._running = True

        # ── Display welcome ──
        header()
        self._show_welcome()

        # ── Prompt session ──
        history = FileHistory("data/chat_history.txt")
        session = PromptSession(
            history=history,
            auto_suggest=AutoSuggestFromHistory(),
            enable_history_search=True,
        )

        while self._running:
            try:
                divider()
                user_input = await session.prompt_async(
                    Text(" You: ", style="accent.bold") + "> ",
                    style="",
                )
            except (EOFError, KeyboardInterrupt):
                console.print()
                console.print(Text(" Goodbye! 👋", style="primary"))
                break

            if not user_input or not user_input.strip():
                continue

            # ── Process input ──
            blank()
            try:
                await self._process_and_render(user_input)
            except SystemExit:
                console.print(Text("\n Shutting down...", style="warning"))
                break
            except Exception as e:
                logger.exception("Chat loop error")
                console.print(
                    Panel(
                        Text(f"❌ Error: {e}", style="error"),
                        border_style="error",
                    )
                )

        # ── Save history ──
        divider()
        console.print(Text(" Session ended. Use /exit to quit, or press Ctrl+C.", style="dim"))

    async def _process_and_render(self, user_input: str) -> None:
        """Route input, stream response, and render."""
        generator = self.router.route(user_input)

        # Show a spinner while waiting for first token
        spinner_task = asyncio.create_task(self._show_spinner())

        full_response = ""
        first_token = True
        async for token in generator:
            if first_token:
                spinner_task.cancel()
                try:
                    await spinner_task
                except asyncio.CancelledError:
                    pass
                console.print(Text(" Agent:", style="agent"))
                console.print(" ", end="")
                sys.stdout.flush()
                first_token = False

            for char in token:
                sys.stdout.write(char)
                sys.stdout.flush()
                await asyncio.sleep(0.004)
                full_response += char

        if first_token:
            spinner_task.cancel()
            try:
                await spinner_task
            except asyncio.CancelledError:
                pass
            console.print(Text(" Agent:", style="agent"))

        console.print()
        blank()

        if full_response:
            self.memory.add_message("assistant", full_response)

    async def _show_spinner(self) -> None:
        """Show a spinner while waiting for first response token."""
        frames = ["|", "/", "-", "\\"]
        i = 0
        try:
            while True:
                sys.stdout.write(f"\r\033[K Thinking... {frames[i]}")
                sys.stdout.flush()
                i = (i + 1) % len(frames)
                await asyncio.sleep(0.12)
        except asyncio.CancelledError:
            sys.stdout.write("\r\033[K")
            sys.stdout.flush()
            raise

    def _show_welcome(self) -> None:
        """Show welcome message with available commands."""
        welcome = (
            "Welcome! I'm your **AI Job Hunting Assistant**.\n\n"
            "I can help you find and apply to jobs across multiple platforms.\n\n"
            "**Commands:**\n"
            "  `/help` — Show all available commands\n"
            "  `/jobhunt` — Interactive job search workflow\n"
            "  `/search` — Quick job search\n"
            "  `/status` — Your application statistics\n"
            "  `/chat` — General career advice & questions\n"
            "  `/agent` — Autonomous agent mode\n"
            "  `/exit` — Quit\n\n"
            "Or just type naturally — I'll understand what you need!"
        )
        console.print(agent_panel(welcome))
        blank()

    def stop(self) -> None:
        self._running = False
