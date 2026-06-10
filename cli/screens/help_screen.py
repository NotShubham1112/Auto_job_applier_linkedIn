"""HelpScreen — modal showing all available commands grouped by category.

Design: minimal. No borders, clean typography hierarchy.
"""

from __future__ import annotations

from rich.text import Text
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Vertical, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Static

from cli.styles.palette import PALETTE, PRODUCT_NAME
from cli.widgets.command_palette import PaletteCommand


class HelpScreen(ModalScreen[None]):
    """Modal help screen showing every command by category."""

    BINDINGS = [
        Binding("escape", "dismiss_help", "Close", show=False),
        Binding("enter", "dismiss_help", "Close", show=False),
        Binding("q", "dismiss_help", "Close", show=False),
    ]

    DEFAULT_CSS = """
    HelpScreen {
        align: center middle;
        background: #000000EE;
    }

    HelpScreen #help-content {
        width: 80;
        height: auto;
        max-height: 80%;
        background: #000000;
        padding: 1 2;
    }

    HelpScreen #help-title {
        color: #ffffff;
        text-style: bold;
        height: 1;
        padding: 0 0 1 0;
        margin-bottom: 1;
    }

    HelpScreen #help-scroll {
        height: auto;
        max-height: 50;
        scrollbar-size: 1 1;
    }

    HelpScreen .help-section-title {
        color: #3b82f6;
        text-style: bold;
        padding: 1 0 0 0;
    }

    HelpScreen .help-row {
        height: 1;
        color: #666666;
    }

    HelpScreen .help-row .help-cmd {
        color: #f43f5e;
        text-style: bold;
        width: 18;
    }

    HelpScreen .help-row .help-desc {
        color: #666666;
    }

    HelpScreen #help-hint {
        color: #444444;
        text-align: center;
        padding: 1 0 0 0;
    }
    """

    def __init__(self, commands: list[PaletteCommand], **kwargs) -> None:
        super().__init__(**kwargs)
        self.commands = commands

    def compose(self) -> ComposeResult:
        with Container(id="help-content"):
            yield Static(
                f" {PRODUCT_NAME}  \u2014  Help ", id="help-title"
            )
            with VerticalScroll(id="help-scroll"):
                yield from self._build_rows()
            yield Static(
                "esc / enter / q  to close",
                id="help-hint",
            )

    def _build_rows(self):
        by_category: dict[str, list[PaletteCommand]] = {}
        for c in self.commands:
            by_category.setdefault(c.category, []).append(c)
        order = ["General", "Job Hunting", "Resume & Documents",
                 "History & Memory", "Developer", "Plugin"]
        cats = [c for c in order if c in by_category]
        for c in by_category:
            if c not in cats:
                cats.append(c)

        for cat in cats:
            yield Static(f" {cat} ", classes="help-section-title")
            for cmd in by_category[cat]:
                row = Static(
                    self._render_row(cmd),
                    classes="help-row",
                )
                yield row

    def _render_row(self, cmd: PaletteCommand) -> Text:
        text = Text()
        text.append(f"  /{cmd.name:<14}", style="bold #f43f5e")
        text.append("  ", style="")
        text.append(cmd.description, style="#666666")
        if cmd.aliases:
            text.append(
                f"   ({', '.join(cmd.aliases)})", style="#666666"
            )
        return text

    def action_dismiss_help(self) -> None:
        self.dismiss(None)
