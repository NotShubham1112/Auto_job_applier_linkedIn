"""BootScreen — animated boot sequence with matrix rain.

Shows the BROWORK logo, a matrix rain animation, then walks through
boot phases with dot-based indicators, then transitions to MainScreen.

Design: minimal. No borders, no decorative elements.
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
from cli.matrix_rain import MatrixRain
from cli.styles.palette import (
    PALETTE,
    PRODUCT_NAME,
    PRODUCT_TAGLINE,
    PRODUCT_VERSION,
)


class _BootLine(Static):
    """A single boot phase line with dot-based indicator."""

    DEFAULT_CSS = """
    _BootLine {
        height: 1;
        color: #444444;
        padding: 0 0;
    }

    _BootLine.done {
        color: #3b82f6;
    }

    _BootLine.active {
        color: #ffffff;
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
            text.append("  \u25cf ", style=f"{PALETTE.primary}")
            text.append(self.label, style=f"{PALETTE.primary}")
        elif state == "active":
            text.append("  \u25cb ", style=f"{PALETTE.accent}")
            text.append(self.label, style=f"bold {PALETTE.text}")
        else:
            text.append("  \u00b7 ", style=f"{PALETTE.text_muted}")
            text.append(self.label, style=f"{PALETTE.text_muted}")
        self.update(text)


class BootScreen(Screen[None]):
    """The initial boot/loading screen.

    Composes the matrix rain animation, BROWORK logo, boot phases,
    and a "Ready." indicator. Transitions to MainScreen when complete.
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

    BootScreen #boot-matrix {
        width: 100%;
        height: 100%;
        color: #3b82f6;
        background: #000000;
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
        padding: 1 0 0 0;
    }

    BootScreen #boot-version {
        color: #666666;
        text-align: center;
        padding: 0 0 1 0;
    }

    BootScreen #boot-list {
        width: auto;
        height: auto;
        padding: 1 0;
    }

    BootScreen #boot-status {
        color: #666666;
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
        self._matrix_widget: Static | None = None
        self._logo_widget: Static | None = None
        self._tagline_widget: Static | None = None
        self._version_widget: Static | None = None
        self._list_widget: Vertical | None = None

    def compose(self) -> ComposeResult:
        with Container(id="boot-container"):
            self._matrix_widget = Static("", id="boot-matrix")
            yield self._matrix_widget
            self._logo_widget = Static(BROWORK_LOGO, id="boot-logo")
            yield self._logo_widget
            self._tagline_widget = Static(PRODUCT_TAGLINE, id="boot-tagline")
            yield self._tagline_widget
            self._version_widget = Static(f"v{PRODUCT_VERSION}", id="boot-version")
            yield self._version_widget
            with Vertical(id="boot-list") as list_widget:
                self._list_widget = list_widget
                for phase_id, label in BOOT_PHASES:
                    line = _BootLine(phase_id, label)
                    self._phase_widgets[phase_id] = line
                    yield line
            self._status_widget = Static("", id="boot-status")
            yield self._status_widget
            self._ready_widget = Static("Ready.", id="boot-ready", classes="hidden")
            yield self._ready_widget

    def on_mount(self) -> None:
        self.run_worker(self._animate_boot(), exclusive=True)

    async def _animate_boot(self) -> None:
        """Matrix rain -> logo reveal -> boot phases -> ready -> transition."""
        # Phase 1: Matrix rain animation (1.2s)
        if self._matrix_widget is not None:
            rain = MatrixRain(width=60, height=20, density=0.25)
            async for frame in rain.frames(duration=1.2, fps=15):
                self._matrix_widget.update(frame)
            self._matrix_widget.update("")

        # Brief pause for clean transition
        await asyncio.sleep(0.15)

        # Phase 2: Boot phases with dot indicators
        status_messages = [
            "initializing runtime",
            "verifying configuration",
            "connecting to data sources",
        ]

        for i, (phase_id, _label) in enumerate(BOOT_PHASES):
            if i > 0:
                prev_id, _ = BOOT_PHASES[i - 1]
                self._phase_widgets[prev_id].set_done()

            self._phase_widgets[phase_id].set_active()

            if self._status_widget is not None and i < len(status_messages):
                self._status_widget.update(
                    Text(f"  {status_messages[i]}", style=PALETTE.text_muted)
                )

            await asyncio.sleep(0.15 + random.random() * 0.12)

        # Mark last phase done
        last_id, _ = BOOT_PHASES[-1]
        self._phase_widgets[last_id].set_done()

        if self._status_widget is not None:
            self._status_widget.update("")

        # Phase 3: Show "Ready."
        if self._ready_widget is not None:
            self._ready_widget.set_class(True, "visible")
            self._ready_widget.set_class(False, "hidden")

        await asyncio.sleep(0.4)

        # Transition to main screen
        if hasattr(self.app, "transition_to_main"):
            self.app.transition_to_main()
            return
        self.app.pop_screen()
