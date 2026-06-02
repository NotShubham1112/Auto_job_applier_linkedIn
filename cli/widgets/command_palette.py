"""CommandPalette — a modal fuzzy-search command picker (ctrl+x).

The palette lists every available slash command. The user can type to
filter, and Enter to run the highlighted command.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional

from rich.text import Text
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Vertical
from textual.screen import ModalScreen
from textual.widgets import Input, Static


@dataclass
class PaletteCommand:
    """One entry in the command palette."""

    name: str           # e.g. "new"
    description: str    # human-readable description
    aliases: list[str] = None  # type: ignore
    category: str = "General"
    run: Optional[Callable[[str], None]] = None

    def __post_init__(self) -> None:
        if self.aliases is None:
            self.aliases = []

    @property
    def search_text(self) -> str:
        return f"{self.name} {' '.join(self.aliases)} {self.description} {self.category}".lower()


class _PaletteRow(Static):
    """A single row inside the palette list."""

    DEFAULT_CSS = """
    _PaletteRow {
        height: 1;
        color: #ffffff;
        padding: 0 1;
    }

    _PaletteRow.--highlight {
        background: #3b82f6;
        color: #ffffff;
        text-style: bold;
    }

    _PaletteRow .palette-cmd {
        color: #f43f5e;
        text-style: bold;
    }

    _PaletteRow .palette-desc {
        color: #ffffff;
    }
    """

    def __init__(self, command: PaletteCommand, **kwargs) -> None:
        # Build the content and pass it via the constructor so the
        # visual is set up correctly before the widget is mounted.
        content = self._build_text(command)
        super().__init__(content, markup=False, **kwargs)
        self.command = command

    def set_highlight(self, on: bool) -> None:
        self.set_class(on, "--highlight")
        # Rebuild and update
        self.update(self._build_text(self.command))

    @staticmethod
    def _build_text(command: PaletteCommand) -> Text:
        text = Text()
        text.append(f" /{command.name:<10}", style="bold #f43f5e")
        text.append("  ", style="")
        text.append(command.description, style="#ffffff")
        if command.aliases:
            text.append("  ", style="")
            text.append(
                f"({', '.join(command.aliases)})", style="#ffffff"
            )
        return text


class CommandPalette(ModalScreen[Optional[str]]):
    """Modal command palette (ctrl+x).

    Dismisses with a result: the chosen command name, or None if the
    user pressed Escape. The caller is responsible for executing the
    command.
    """

    BINDINGS = [
        Binding("escape", "dismiss_palette", "Cancel", show=False),
        Binding("up", "move_up", "Up", show=False),
        Binding("down", "move_down", "Down", show=False),
        Binding("enter", "select", "Select", show=False),
    ]

    DEFAULT_CSS = """
    CommandPalette {
        align: center middle;
        background: #000000;
    }

    CommandPalette #palette-container {
        width: 70;
        height: auto;
        max-height: 24;
        background: #000000;
        border: round #3b82f6;
        padding: 1 1;
    }

    CommandPalette #palette-title {
        color: #3b82f6;
        text-style: bold;
        height: 1;
        padding: 0 1;
    }

    CommandPalette #palette-input {
        height: 3;
        background: #000000;
        color: #ffffff;
        border: tall #3b82f6;
        margin: 1 0;
        padding: 0 1;
    }

    CommandPalette #palette-input:focus {
        border: tall #f43f5e;
    }

    CommandPalette #palette-input > .input--placeholder {
        color: #ffffff;
        text-style: italic;
    }

    CommandPalette #palette-list {
        height: auto;
        max-height: 16;
        background: #000000;
        border: round #3b82f6;
        padding: 0 1;
        scrollbar-size: 1 1;
    }

    CommandPalette #palette-hint {
        color: #ffffff;
        height: 1;
        padding: 0 1;
        margin-top: 1;
    }
    """

    def __init__(self, commands: list[PaletteCommand], **kwargs) -> None:
        super().__init__(**kwargs)
        self.all_commands = commands
        self.filtered: list[PaletteCommand] = list(commands)
        self.highlight_index = 0
        self._row_widgets: list[_PaletteRow] = []
        self._input_widget: Optional[Input] = None

    def compose(self) -> ComposeResult:
        with Container(id="palette-container"):
            yield Static(" BROWORK \u2014 Command Palette ", id="palette-title")
            self._input_widget = Input(
                placeholder="Type a command...",
                id="palette-input",
            )
            yield self._input_widget
            with Vertical(id="palette-list"):
                for cmd in self.filtered:
                    row = _PaletteRow(cmd)
                    self._row_widgets.append(row)
                    yield row
            yield Static(
                "\u2191\u2193 navigate  \u23ce select  esc close",
                id="palette-hint",
            )

    def on_mount(self) -> None:
        self._update_highlight()
        if self._input_widget is not None:
            self._input_widget.focus()

    def on_input_changed(self, event: Input.Changed) -> None:
        query = event.value.strip().lower()
        if not query:
            self.filtered = list(self.all_commands)
        else:
            self.filtered = [
                c for c in self.all_commands
                if self._matches(c.search_text, query)
            ]
        self.highlight_index = 0
        self._rebuild_rows()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """When the user presses Enter in the search input, select."""
        self.action_select()

    def _matches(self, haystack: str, needle: str) -> bool:
        # Simple fuzzy match: all characters of needle must appear in order
        hi = 0
        for ch in needle:
            found = haystack.find(ch, hi)
            if found == -1:
                return False
            hi = found + 1
        return True

    def _rebuild_rows(self) -> None:
        for w in self._row_widgets:
            w.remove()
        self._row_widgets = []
        list_widget = self.query_one("#palette-list")
        for cmd in self.filtered:
            row = _PaletteRow(cmd)
            self._row_widgets.append(row)
            list_widget.mount(row)
        if self.filtered:
            self._update_highlight()
        self.refresh(layout=True)

    def _update_highlight(self) -> None:
        for i, row in enumerate(self._row_widgets):
            row.set_highlight(i == self.highlight_index)

    # ── Actions ────────────────────────────────────────────────────────

    def action_dismiss_palette(self) -> None:
        self.dismiss(None)

    def action_move_up(self) -> None:
        if not self.filtered:
            return
        self.highlight_index = (self.highlight_index - 1) % len(self.filtered)
        self._update_highlight()

    def action_move_down(self) -> None:
        if not self.filtered:
            return
        self.highlight_index = (self.highlight_index + 1) % len(self.filtered)
        self._update_highlight()

    def action_select(self) -> None:
        if not self.filtered:
            self.dismiss(None)
            return
        chosen = self.filtered[self.highlight_index]
        self.dismiss(chosen.name)
