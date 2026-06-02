"""BootScreen — the initial screen that shows the BROWORK logo and
runs through the boot phases (Loading Models, Agents, Memory, ...).

This screen is shown for ~600-1500ms, then the app transitions to the
main chat screen.
"""

from __future__ import annotations

import asyncio
import random

from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.screen import Screen
from textual.widgets import Static

from cli.banner import BROWORK_LOGO, BOOT_PHASES, render_boot_phase
from cli.styles.palette import (
    PALETTE,
    PRODUCT_NAME,
    PRODUCT_TAGLINE,
    PRODUCT_VERSION,
)


class _BootLine(Static):
    """A single 'Loading Models' / 'Loading Agents' / ... line."""

    DEFAULT_CSS = """
    _BootLine {
        height: 1;
        color: #9a9a9a;
        padding: 0 1;
    }

    _BootLine.done {
        color: #7ee787;
    }

    _BootLine.active {
        color: #f4b183;
        text-style: bold;
    }
    """

    def __init__(self, phase_id: str, label: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self.phase_id = phase_id
        self.label = label
        self._render_state("pending")

    def set_active(self) -> None:
        self._render_state("active")

    def set_done(self) -> None:
        self._render_state("done")

    def _render_state(self, state: str) -> None:
        for cls in ("done", "active", "pending"):
            self.set_class(state == cls, cls)
        text = Text()
        if state == "done":
            text.append("  [+] ", style="#3b82f6")
            text.append(self.label, style="#3b82f6")
        elif state == "active":
            text.append("  [~] ", style="#ffffff")
            text.append(self.label, style="bold #ffffff")
        else:
            text.append("  [ ] ", style="#ffffff")
            text.append(self.label, style="#ffffff")
        self.update(text)


class BootScreen(Screen[None]):
    """The initial boot/loading screen.

    Composes the BROWORK logo, a tagline, the list of loading phases,
    and a "Ready." line that appears at the end.
    """

    DEFAULT_CSS = """
    BootScreen {
        background: #000000;
        align: center middle;
    }

    BootScreen #boot-container {
        width: auto;
        height: auto;
        align: center middle;
    }

    BootScreen #boot-logo {
        color: #3b82f6;
        text-style: bold;
        width: auto;
        content-align: center middle;
    }

    BootScreen #boot-tagline {
        color: #ffffff;
        text-align: center;
        padding: 1 0;
    }

    BootScreen #boot-version {
        color: #ffffff;
        text-align: center;
        padding: 0 0 1 0;
    }

    BootScreen #boot-list {
        width: 50;
        height: auto;
        padding: 1 2;
    }

    BootScreen #boot-status {
        color: #ffffff;
        text-align: center;
        padding: 1 0 0 0;
    }

    BootScreen #boot-ready {
        color: #f43f5e;
        text-align: center;
        text-style: bold;
        padding: 1 0 0 0;
        height: 1;
    }

    BootScreen #boot-ready.visible {
        visibility: visible;
    }

    BootScreen #boot-ready.hidden {
        visibility: hidden;
    }
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._phase_widgets: dict[str, _BootLine] = {}
        self._status_widget: Static | None = None
        self._ready_widget: Static | None = None

    def compose(self) -> ComposeResult:
        with Container(id="boot-container"):
            yield Static(BROWORK_LOGO, id="boot-logo")
            yield Static(PRODUCT_TAGLINE, id="boot-tagline")
            yield Static(f"v{PRODUCT_VERSION}", id="boot-version")
            with Vertical(id="boot-list"):
                for phase_id, label in BOOT_PHASES:
                    line = _BootLine(phase_id, label)
                    self._phase_widgets[phase_id] = line
                    yield line
            self._status_widget = Static("", id="boot-status")
            yield self._status_widget
            self._ready_widget = Static("Ready.", id="boot-ready", classes="hidden")
            yield self._ready_widget

    def on_mount(self) -> None:
        # Kick off the boot animation
        self.run_worker(self._animate_boot(), exclusive=True)

    async def _animate_boot(self) -> None:
        """Walk through each boot phase, marking active then done."""
        status_messages = [
            "Initializing runtime...",
            "Verifying configuration...",
            "Connecting to data sources...",
        ]

        for i, (phase_id, _label) in enumerate(BOOT_PHASES):
            # Mark previous as done
            if i > 0:
                prev_id, _ = BOOT_PHASES[i - 1]
                self._phase_widgets[prev_id].set_done()

            # Mark this one active
            self._phase_widgets[phase_id].set_active()

            # Rotate a status message
            if self._status_widget is not None and i < len(status_messages):
                self._status_widget.update(
                    Text(f"\u26a1 {status_messages[i]}", style="#58a6ff")
                )

            # Slight randomized delay so each boot feels alive
            await asyncio.sleep(0.18 + random.random() * 0.18)

        # Mark the last phase done
        last_id, _ = BOOT_PHASES[-1]
        self._phase_widgets[last_id].set_done()

        if self._status_widget is not None:
            self._status_widget.update("")

        if self._ready_widget is not None:
            self._ready_widget.set_class(True, "visible")
            self._ready_widget.set_class(False, "hidden")

        # Brief pause so the user can read "Ready."
        await asyncio.sleep(0.35)

        # Hand off to the main screen
        if hasattr(self.app, "transition_to_main"):
            self.app.transition_to_main()
            return
        # Fallback: just pop this screen
        self.app.pop_screen()
