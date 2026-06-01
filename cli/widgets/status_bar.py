"""StatusBar widget — bottom status line with model/tokens/mode info.

Displays cells like:
    MODEL: Claude-4 │ TOKENS: 15K │ COST: $0.08 │ PLAN MODE

Cells are reactive and can be updated individually.
"""

from __future__ import annotations

from typing import Optional

from rich.text import Text
from textual.containers import Horizontal
from textual.reactive import reactive
from textual.widgets import Static

from cli.styles.palette import PALETTE, PRODUCT_NAME, PRODUCT_VERSION


class StatusCell(Static):
    """A single cell in the status bar.

    The cell is a small Static widget. It can have one of a few
    visual styles ('accent', 'success', 'info', 'warning').
    """

    DEFAULT_CSS = """
    StatusCell {
        height: 1;
        padding: 0 2;
        color: #9a9a9a;
    }

    StatusCell.accent {
        color: #f4b183;
        text-style: bold;
    }

    StatusCell.success {
        color: #7ee787;
    }

    StatusCell.info {
        color: #58a6ff;
    }

    StatusCell.warning {
        color: #e3b341;
    }
    """

    def __init__(self, label: str, value: str = "", style: str = "", **kwargs) -> None:
        super().__init__(**kwargs)
        self._label = label
        self._value = value
        self._style = style
        if style:
            self.add_class(style)

    def set_value(self, value: str) -> None:
        self._value = value
        self.update(self._render())

    def _render(self) -> Text:
        text = Text()
        text.append(f"{self._label}: ", style="#6a6a6a")
        text.append(self._value, style="")
        return text

    def on_mount(self) -> None:
        self.update(self._render())


class StatusSpacer(Static):
    """A flexible-width empty cell used to push cells to the right."""

    DEFAULT_CSS = """
    StatusSpacer {
        width: 1fr;
        height: 1;
    }
    """

    def render(self) -> str:
        return ""


class StatusBar(Horizontal):
    """The bottom status bar of the BROWORK app.

    Layout (left to right):
        MODEL | TOKENS | COST | MODE   ...spacer...   MCP | MEMORY | SESSION

    Cells are exposed as named attributes for easy updates from the
    app: ``self.status_bar.model.set_value("Claude-4")``.
    """

    DEFAULT_CSS = """
    StatusBar {
        dock: bottom;
        height: 1;
        background: #141414;
        color: #9a9a9a;
        padding: 0 1;
        border-top: solid #2a2a2a;
    }
    """

    model_name: reactive[str] = reactive("loading...")
    tokens: reactive[str] = reactive("0")
    cost: reactive[str] = reactive("$0.00")
    mode: reactive[str] = reactive("PLAN MODE")
    mcp: reactive[str] = reactive("0")
    memory: reactive[str] = reactive("ENABLED")
    session: reactive[str] = reactive("0h 0m")
    brand: reactive[str] = reactive(f"{PRODUCT_NAME} v{PRODUCT_VERSION}")

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.model: Optional[StatusCell] = None
        self.tokens_cell: Optional[StatusCell] = None
        self.cost_cell: Optional[StatusCell] = None
        self.mode_cell: Optional[StatusCell] = None
        self.mcp_cell: Optional[StatusCell] = None
        self.memory_cell: Optional[StatusCell] = None
        self.session_cell: Optional[StatusCell] = None
        self.brand_cell: Optional[StatusCell] = None

    def compose(self):
        self.brand_cell = StatusCell("", self.brand, classes="accent")
        yield self.brand_cell
        yield StatusCell("", "│", classes="")

        self.model = StatusCell("MODEL", self.model_name, classes="accent")
        yield self.model
        yield StatusCell("", "│")

        self.tokens_cell = StatusCell("TOKENS", self.tokens)
        yield self.tokens_cell
        yield StatusCell("", "│")

        self.cost_cell = StatusCell("COST", self.cost)
        yield self.cost_cell
        yield StatusCell("", "│")

        self.mode_cell = StatusCell("MODE", self.mode, classes="info")
        yield self.mode_cell

        yield StatusSpacer()

        self.memory_cell = StatusCell("MEMORY", self.memory, classes="success")
        yield self.memory_cell
        yield StatusCell("", "│")

        self.mcp_cell = StatusCell("MCP", self.mcp)
        yield self.mcp_cell
        yield StatusCell("", "│")

        self.session_cell = StatusCell("SESSION", self.session)
        yield self.session_cell

    # ── Reactive watchers ──────────────────────────────────────────────

    def watch_model_name(self, _old: str, new: str) -> None:
        if self.model is not None:
            self.model.set_value(new)

    def watch_tokens(self, _old: str, new: str) -> None:
        if self.tokens_cell is not None:
            self.tokens_cell.set_value(new)

    def watch_cost(self, _old: str, new: str) -> None:
        if self.cost_cell is not None:
            self.cost_cell.set_value(new)

    def watch_mode(self, _old: str, new: str) -> None:
        if self.mode_cell is not None:
            self.mode_cell.set_value(new)

    def watch_mcp(self, _old: str, new: str) -> None:
        if self.mcp_cell is not None:
            self.mcp_cell.set_value(new)

    def watch_memory(self, _old: str, new: str) -> None:
        if self.memory_cell is not None:
            self.memory_cell.set_value(new)

    def watch_session(self, _old: str, new: str) -> None:
        if self.session_cell is not None:
            self.session_cell.set_value(new)

    def watch_brand(self, _old: str, new: str) -> None:
        if self.brand_cell is not None:
            self.brand_cell.set_value(new)
