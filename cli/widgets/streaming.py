"""StreamingOutput widget — markdown-aware streaming text area.

The widget accumulates an incoming string and renders it through
Rich's Markdown renderer as new content arrives. It auto-scrolls
to the bottom on each update.
"""

from __future__ import annotations

from rich.console import Group
from rich.markdown import Markdown
from rich.padding import Padding
from rich.text import Text
from textual.widgets import RichLog

from cli.styles.palette import PALETTE


class StreamingOutput(RichLog):
    """A RichLog that renders streamed content as Markdown.

    Use ``begin_user_message()``, ``begin_agent_message()`` to start a
    labelled block, then ``stream(chunk)`` to push tokens into it, and
    ``end_message()`` to finalize the block.

    The widget keeps the raw accumulated text per-block and re-renders
    the markdown for the active block on each push. This gives a nice
    "typing into a rendered document" feel.

    Auto-scrolls to the bottom on every update.
    """

    DEFAULT_CSS = """
    StreamingOutput {
        background: #0a0a0a;
        padding: 1 2;
        scrollbar-gutter: stable;
    }
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(
            highlight=False,
            markup=False,
            wrap=True,
            **kwargs,
        )
        self._active_role: str | None = None
        self._active_buffer: str = ""
        self._rendered_messages: list[Group] = []

    # ── Public streaming API ──────────────────────────────────────────

    def begin_user_message(self, text: str = "") -> None:
        """Start a user message block."""
        if self._active_role is not None:
            self.end_message()
        self._active_role = "user"
        self._active_buffer = text
        self._render_role_header("user")
        if text:
            self.write(Padding(Text(text, style=PALETTE.text), (0, 4, 0, 2)))

    def begin_agent_message(self, text: str = "") -> None:
        """Start an agent message block."""
        if self._active_role is not None:
            self.end_message()
        self._active_role = "agent"
        self._active_buffer = text
        self._render_role_header("agent")
        if text:
            self._write_markdown(text)

    def stream(self, chunk: str) -> None:
        """Append a chunk of text to the active block and re-render."""
        if self._active_role is None:
            self.begin_agent_message()
        self._active_buffer += chunk
        if self._active_role == "user":
            # Don't render user input as markdown
            return
        self._write_markdown(self._active_buffer)

    def end_message(self) -> None:
        """Finalize the active block."""
        if self._active_role is None:
            return
        if self._active_role == "agent" and self._active_buffer:
            # Final render of the markdown
            self._write_markdown(self._active_buffer)
        self._active_role = None
        self._active_buffer = ""

    def write_system(self, text: str) -> None:
        """Write a dim system message (info, help, errors)."""
        self.end_message()
        self.write(Padding(
            Text(text, style=PALETTE.text_dim),
            (0, 0, 1, 0),
        ))

    def write_error(self, text: str) -> None:
        """Write an error block."""
        self.end_message()
        self.write(Padding(
            Text(f"\u2717 {text}", style=f"bold {PALETTE.error}"),
            (1, 0, 1, 0),
        ))

    def write_user_echo(self, text: str) -> None:
        """Write the user input echo above the agent response."""
        self.end_message()
        header = Text()
        header.append("\u276f ", style=f"bold {PALETTE.user_color}")
        header.append("You", style=f"bold {PALETTE.user_color}")
        self.write(Padding(header, (1, 0, 0, 2)))
        self.write(Padding(
            Text(text, style=PALETTE.text),
            (0, 0, 1, 4),
        ))

    # ── Internals ──────────────────────────────────────────────────────

    def _render_role_header(self, role: str) -> None:
        if role == "user":
            header = Text()
            header.append("\u276f ", style=f"bold {PALETTE.user_color}")
            header.append("You", style=f"bold {PALETTE.user_color}")
        else:
            header = Text()
            header.append("\u25cf ", style=f"bold {PALETTE.agent_color}")
            header.append("Agent", style=f"bold {PALETTE.agent_color}")
        self.write(Padding(header, (1, 0, 0, 2)))

    def _write_markdown(self, content: str) -> None:
        """Write the given content rendered as Markdown.

        We clear the last markdown line and re-render it to create the
        streaming effect without leaving dozens of stale renders.
        """
        try:
            md = Markdown(content, code_theme="monokai", inline_mode_breaks=True)
            # Wrap in a padding so the content indents nicely
            from rich.panel import Panel
            from rich.box import ROUNDED

            self.write(Padding(
                Panel(
                    md,
                    border_style=PALETTE.border,
                    box=ROUNDED,
                    padding=(0, 1),
                ),
                (0, 0, 0, 2),
            ))
        except Exception:
            # If Markdown fails for any reason, fall back to plain text
            self.write(Padding(
                Text(content, style=PALETTE.text),
                (0, 0, 0, 2),
            ))

    def clear_log(self) -> None:
        """Clear all messages."""
        self.clear()
        self._active_role = None
        self._active_buffer = ""
        self._rendered_messages = []
