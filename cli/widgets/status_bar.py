"""StatusBar widget — bottom status line with model/tokens/mode info.

Displays cells like:
    BROWORK v1.0.0  model  tokens  cost  ...  memory  session

Cells are reactive and can be updated individually.
Design: minimal. No borders, muted colors, thin separators.
"""

from __future__ import annotations

from typing import Optional

from rich.text import Text as RichText
from textual.containers import Horizontal
from textual.reactive import reactive
from textual.widgets import Static

from cli.styles.palette import PALETTE, PRODUCT_NAME, PRODUCT_VERSION


class StatusCell(Static):
    """A single cell in the status bar."""

    DEFAULT_CSS = """
    StatusCell {
        height: 1;
        padding: 0 1;
        color: #666666;
    }

    StatusCell.accent {
        color: #f43f5e;
        text-style: bold;
    }

    StatusCell.success {
        color: #3b82f6;
    }

    StatusCell.info {
        color: #3b82f6;
    }

    StatusCell.warning {
        color: #f43f5e;
    }
    """

    def __init__(self, label: str, value: str = "", style: str = "", **kwargs) -> None:
        super().__init__(**kwargs)
        self._label = label
        self._value = value
        self._style = style
        if style:
            self.add_class(style)
        self.update(self._build_text())

    def set_value(self, value: str) -> None:
        self._value = value
        self.update(self._build_text())

    def _build_text(self) -> RichText:
        text = RichText()
        if self._label:
            text.append(f"{self._label} ", style=PALETTE.text_muted)
        text.append(self._value, style="")
        return text


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
        BRAND  model  tokens  cost  ...  memory  session

    Cells are exposed as named attributes for easy updates.
    """

    DEFAULT_CSS = """
    StatusBar {
        dock: bottom;
        height: 1;
        background: #000000;
        color: #666666;
        padding: 0 2;
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

        self.model = StatusCell("model", self.model_name, classes="info")
        yield self.model

        self.tokens_cell = StatusCell("tokens", self.tokens)
        yield self.tokens_cell

        self.cost_cell = StatusCell("cost", self.cost)
        yield self.cost_cell

        self.mode_cell = StatusCell("mode", self.mode, classes="info")
        yield self.mode_cell

        yield StatusSpacer()

        self.memory_cell = StatusCell("memory", self.memory, classes="success")
        yield self.memory_cell

        self.mcp_cell = StatusCell("mcp", self.mcp)
        yield self.mcp_cell

        self.session_cell = StatusCell("session", self.session)
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
