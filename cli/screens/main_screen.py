"""MainScreen — the post-boot chat screen.

Layout (vertical stack, top-to-bottom):
  1. Header bar (brand + session info)
  2. Content (horizontal split):
     - left: ThinkingBox + StreamingOutput (chat log)
     - right: AgentBoard
  3. Input area (Textual Input + hint)
  4. StatusBar (docked bottom)

Key bindings:
  ctrl+x — open command palette
  ctrl+c — exit
  ctrl+l — clear log
"""

from __future__ import annotations

import datetime as dt
import logging
from typing import Any, Optional

from rich.text import Text
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import Input, Static

from chat.memory import ConversationMemory
from chat.router import CommandRouter
from cli.commands import build_static_commands, commands_to_palette
from cli.router_bridge import build_router, stream_router_to_app
from cli.screens.help_screen import HelpScreen
from cli.styles.palette import (
    PALETTE,
    PRODUCT_NAME,
    PRODUCT_VERSION,
)
from cli.widgets.agent_board import (
    AGENT_DONE,
    AGENT_RUNNING,
    AGENT_WAITING,
    AgentEntry,
)
from cli.widgets.command_palette import CommandPalette, PaletteCommand
from cli.widgets.status_bar import StatusBar
from cli.widgets.streaming import StreamingOutput
from cli.widgets.thinking import ThinkingBox

logger = logging.getLogger(__name__)


class MainScreen(Screen[None]):
    """The main chat screen shown after the boot sequence."""

    BINDINGS = [
        Binding("ctrl+p", "open_palette", "Palette", show=True, priority=True),
        Binding("ctrl+x", "open_palette", "Palette", show=False, priority=True),
        Binding("ctrl+c", "quit_app", "Quit", show=True, priority=True),
        Binding("ctrl+l", "clear_log", "Clear", show=False, priority=True),
        Binding("ctrl+question_mark", "show_help", "Help", show=False),
        Binding("f1", "show_help", "Help", show=False),
    ]

    DEFAULT_CSS = """
    MainScreen {
        layout: vertical;
        background: #000000;
    }

    MainScreen #main-header {
        height: 1;
        background: #000000;
        color: #ffffff;
        text-style: bold;
        padding: 0 2;
        border-bottom: solid #3b82f6;
    }

    MainScreen #main-content {
        layout: horizontal;
        height: 1fr;
        background: #000000;
    }

    MainScreen #chat-column {
        layout: vertical;
        width: 1fr;
        background: #000000;
    }

    MainScreen #thinking-host {
        height: auto;
        padding: 0 2;
    }

    MainScreen #thinking-host.hidden {
        display: none;
    }

    MainScreen #log-container {
        height: 1fr;
        background: #000000;
        scrollbar-size: 1 1;
    }

    MainScreen #loading-indicator {
        height: 1;
        color: #3b82f6;
        padding: 0 4;
        visibility: hidden;
    }

    MainScreen #loading-indicator.visible {
        visibility: visible;
    }

    MainScreen #loading-spinner {
        color: #f43f5e;
        text-style: bold;
        width: 3;
    }

    MainScreen #loading-text {
        color: #3b82f6;
    }

    MainScreen #agent-column {
        width: 38;
        background: #000000;
    }

    MainScreen #agent-column.hidden {
        display: none;
    }

    MainScreen #input-area {
        height: auto;
        background: #000000;
        border-top: solid #3b82f6;
        padding: 0 1;
    }

    MainScreen #input-box {
        height: 3;
        background: #000000;
        color: #ffffff;
        border: tall #3b82f6;
        padding: 0 1;
    }

    MainScreen #input-box:focus {
        border: tall #f43f5e;
    }

    MainScreen #input-box > .input--cursor {
        color: #f43f5e;
        background: #f43f5e;
        text-style: bold;
    }

    MainScreen #input-box > .input--placeholder {
        color: #ffffff;
        text-style: italic;
    }

    MainScreen #input-prefix {
        color: #f43f5e;
        text-style: bold;
        width: 3;
    }

    MainScreen #input-hint {
        color: #ffffff;
        height: 1;
        padding: 0 2;
    }
    """

    def __init__(
        self,
        *,
        config,
        router: CommandRouter,
        registry,
        memory: ConversationMemory,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.config = config
        self.router = router
        self.registry = registry
        self.memory = memory

        # Widget refs (populated in compose)
        self.chat_output: Optional[StreamingOutput] = None
        self.thinking: Optional[ThinkingBox] = None
        self.thinking_host: Optional[Container] = None
        self.input: Optional[Input] = None
        self.status_bar: Optional[StatusBar] = None
        self.agent_board: Optional[Any] = None
        self.loading_indicator: Optional[Horizontal] = None
        self.loading_text: Optional[Static] = None

        self._session_start: dt.datetime = dt.datetime.utcnow()
        self._token_count: int = 0
        self._busy: bool = False

    # ── Compose ────────────────────────────────────────────────────────

    def compose(self) -> ComposeResult:
        # Header
        with Horizontal(id="main-header"):
            yield Static(
                f"  {PRODUCT_NAME}  \u2022  AI Engineering Workspace  "
                f"\u2022  v{PRODUCT_VERSION}",
            )

        with Horizontal(id="main-content"):
            # Left column: chat
            with Vertical(id="chat-column"):
                with Container(id="thinking-host"):
                    self.thinking = ThinkingBox(id="thinking-box")
                    yield self.thinking
                with VerticalScroll(id="log-container"):
                    self.chat_output = StreamingOutput(id="chat-log")
                    yield self.chat_output
                self.loading_indicator = Horizontal(
                    Static("\u280b", id="loading-spinner"),
                    Static("Thinking...", id="loading-text"),
                    id="loading-indicator",
                )
                yield self.loading_indicator

            # Right column: agent board
            from cli.widgets.agent_board import AgentBoard
            with Vertical(id="agent-column"):
                self.agent_board = AgentBoard()
                yield self.agent_board

        # Input area
        with Vertical(id="input-area"):
            with Horizontal():
                yield Static("\u276f", id="input-prefix")
                self.input = Input(
                    placeholder="Ask anything, or type / for commands",
                    id="input-box",
                )
                yield self.input
            yield Static(
                "enter send  \u2022  / for commands  \u2022  "
                "ctrl+x palette  \u2022  ctrl+l clear  \u2022  "
                "ctrl+c quit",
                id="input-hint",
            )

        # Status bar (docked)
        self.status_bar = StatusBar(id="status-bar")
        yield self.status_bar

    def on_mount(self) -> None:
        # Initial state
        if self.thinking is not None:
            self.thinking.display = False
            self.thinking_host_display(False)
        if self.input is not None:
            self.input.focus()
        # Seed status bar with current model
        self._update_status_model()
        self._update_status_tokens()
        # Show welcome banner
        self._show_welcome()

    # ── Helpers for show/hide the thinking host ───────────────────────

    def thinking_host_display(self, show: bool) -> None:
        if self.thinking_host is None:
            return
        try:
            host = self.query_one("#thinking-host")
        except Exception:
            return
        if show:
            host.set_class(False, "hidden")
        else:
            host.set_class(True, "hidden")

    # ── Status bar updates ────────────────────────────────────────────

    def _update_status_model(self) -> None:
        if self.status_bar is None:
            return
        model_name = getattr(
            self.config.ai.groq_model, "value", str(self.config.ai.groq_model)
        )
        # Shorten for display
        short = model_name.split("/")[-1] if "/" in model_name else model_name
        self.status_bar.model_name = short

    def _update_status_tokens(self) -> None:
        if self.status_bar is None:
            return
        if self._token_count < 1000:
            text = str(self._token_count)
        else:
            text = f"{self._token_count / 1000:.1f}K"
        self.status_bar.tokens = text

    def _update_status_session(self) -> None:
        if self.status_bar is None:
            return
        elapsed = dt.datetime.utcnow() - self._session_start
        hours, rem = divmod(int(elapsed.total_seconds()), 3600)
        minutes = rem // 60
        self.status_bar.session = f"{hours}h {minutes}m"

    # ── Welcome / status messages ─────────────────────────────────────

    def _show_welcome(self) -> None:
        if self.chat_output is None:
            return
        self.chat_output.write_system(
            f"{PRODUCT_NAME} ready.  Type /help to see commands, "
            f"or just start typing."
        )
        from rich.padding import Padding
        from rich.text import Text as RichText
        from rich.panel import Panel
        from rich.box import ROUNDED

        title = RichText(
            " AI Job Hunting Assistant  \u2014  Press ctrl+x for the "
            "command palette",
            style=f"bold {PALETTE.primary}",
        )
        body_lines = []
        for cmd, desc in [
            ("/jobhunt", "Run the full job hunt workflow"),
            ("/search", "Quick job search"),
            ("/status", "Your application statistics"),
            ("/chat", "General career chat mode"),
            ("/agent", "Autonomous agent mode"),
        ]:
            line = RichText()
            line.append(f"  {cmd:<12}", style=f"bold {PALETTE.command_color}")
            line.append(f"  {desc}", style=PALETTE.text)
            body_lines.append(line)

        body = RichText()
        body.append_text(title)
        body.append("\n")
        for bl in body_lines:
            body.append_text(bl)
            body.append("\n")

        self.chat_output.write(Padding(Panel(
            body,
            border_style=PALETTE.border,
            box=ROUNDED,
            padding=(1, 2),
        ), (0, 2, 1, 2)))

    # ── Input handling ────────────────────────────────────────────────

    def on_input_submitted(self, event: Input.Submitted) -> None:
        text = event.value.strip()
        if not text:
            return
        # Clear the input field for the next message
        event.input.value = ""
        # Schedule the dispatch as a worker so the UI can refresh
        self.run_worker(self._dispatch(text), exclusive=True)

    async def _dispatch(self, text: str) -> None:
        """Dispatch a user input through the router."""
        if self._busy:
            # If we're already busy, queue the input
            if self.chat_output is not None:
                self.chat_output.write_system(
                    "Busy with previous request — try again in a moment."
                )
            return
        self._busy = True

        # 1. Echo the user input
        if self.chat_output is not None:
            self.chat_output.write_user_echo(text)

        # 2. Pre-emptively show the thinking box for slash commands
        if text.startswith("/"):
            self._show_thinking_for_command(text)

        # 3. Stream the response
        try:
            await stream_router_to_app(
                self.router,
                text,
                on_token=self._on_token,
                on_status=self._on_status,
                on_finish=self._on_finish,
            )
        except SystemExit:
            self._busy = False
            self.app.exit()
            return
        except Exception as e:
            logger.exception("Dispatch failed")
            if self.chat_output is not None:
                self.chat_output.write_error(str(e))
        finally:
            self._busy = False
            # Hide the thinking box and loading indicator
            if self.thinking is not None:
                self.thinking.display = False
                self.thinking_host_display(False)
            self._set_loading_visible(False)
            if self.input is not None:
                self.input.focus()

    # ── Streaming callbacks ───────────────────────────────────────────

    def _on_token(self, token: str) -> None:
        if self.chat_output is None:
            return
        # Start the agent block on the very first token
        if not self.chat_output._active_role:
            self.chat_output.begin_agent_message()
        self.chat_output.stream(token)
        # Approximate token count (rough heuristic: ~4 chars per token)
        self._token_count += max(1, len(token) // 4)
        self._update_status_tokens()

    def _on_status(self, message: str) -> None:
        if not message:
            self._set_loading_visible(False)
            return
        self._set_loading_visible(True)
        if self.loading_text is not None:
            self.loading_text.update(message)

    def _on_finish(self, full: str) -> None:
        if self.chat_output is None:
            return
        self.chat_output.end_message()
        if full:
            self.memory.add_message("assistant", full)
        # Update session timer
        self._update_status_session()

    # ── Loading indicator helpers ─────────────────────────────────────

    def _set_loading_visible(self, visible: bool) -> None:
        if self.loading_indicator is None:
            return
        try:
            ind = self.query_one("#loading-indicator")
        except Exception:
            return
        if visible:
            ind.set_class(True, "visible")
        else:
            ind.set_class(False, "visible")

    # ── Thinking box setup for commands ───────────────────────────────

    def _show_thinking_for_command(self, text: str) -> None:
        """Populate the thinking box with a generic plan for a command."""
        if self.thinking is None:
            return
        cmd = text.split()[0].lstrip("/")
        if cmd in {"help", "clear", "exit", "models", "agents", "memory", "settings"}:
            return  # no thinking needed
        if self.thinking is not None:
            self.thinking.set_steps([
                "Routing command",
                "Resolving plugin",
                "Executing",
            ])
            self.thinking.display = True
            self.thinking_host_display(True)
            self.thinking.start(0)

    # ── Bindings / actions ────────────────────────────────────────────

    def action_open_palette(self) -> None:
        static = build_static_commands()
        plugin_cmds = self.registry.commands_list()
        all_cmds = commands_to_palette(static, plugin_cmds)

        def _on_dismiss(result: Optional[str]) -> None:
            if result:
                # Put the command into the input box
                if self.input is not None:
                    self.input.value = f"/{result} "
                    self.input.focus()

        self.app.push_screen(CommandPalette(all_cmds), _on_dismiss)

    def action_quit_app(self) -> None:
        self.app.exit()

    def action_clear_log(self) -> None:
        if self.chat_output is not None:
            self.chat_output.clear_log()
        self._token_count = 0
        self._update_status_tokens()

    def action_show_help(self) -> None:
        static = build_static_commands()
        plugin_cmds = self.registry.commands_list()
        all_cmds = commands_to_palette(static, plugin_cmds)
        self.app.push_screen(HelpScreen(all_cmds))
