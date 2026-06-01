from __future__ import annotations

import asyncio
import sys
from contextlib import contextmanager
from typing import Any, AsyncGenerator, Optional

from rich.align import Align
from rich.box import Box, HEAVY_EDGE, MINIMAL, ROUNDED
from rich.columns import Columns
from rich.console import Console, Group
from rich.layout import Layout
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)
from rich.rule import Rule
from rich.spinner import Spinner
from rich.style import Style
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text
from rich.tree import Tree

from ui.styles import CUSTOM_THEME, Palette

console = Console(theme=CUSTOM_THEME, highlight=False)
err_console = Console(stderr=True, theme=CUSTOM_THEME)

# ── Shared progress ─────────────────────────────────────────────────────────
_spinner_style = Style(color=Palette.PRIMARY)
_progress_style = Style(color=Palette.SECONDARY)


def make_spinner(message: str = "") -> Progress:
    return Progress(
        SpinnerColumn(spinner_name="dots", style=_spinner_style),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    )


def make_progress(description: str = "") -> Progress:
    return Progress(
        SpinnerColumn(spinner_name="dots", style=_spinner_style),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(bar_width=40, style=_progress_style, completed_style=Style(color=Palette.PRIMARY)),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console,
    )


# ── Panels ───────────────────────────────────────────────────────────────────


def agent_panel(content: str | Any, title: str = "Agent") -> Panel:
    if isinstance(content, str):
        content = Text(content, style="text")
    return Panel(
        content,
        title=Text(f" {title} ", style="agent"),
        border_style="secondary",
        box=ROUNDED,
        padding=(1, 2),
        subtitle=Text("───", style="dim"),
    )


def user_panel(content: str) -> Panel:
    return Panel(
        Text(content, style="text"),
        title=Text(" You ", style="user"),
        border_style="accent",
        box=ROUNDED,
        padding=(0, 2),
    )


def status_panel(groq_ok: bool = False, linkedin_ok: bool = False, resume_ok: bool = False) -> Panel:
    items = [
        f"{'✅' if groq_ok else '❌'} Groq {'Connected' if groq_ok else 'Disconnected'}",
        f"{'✅' if linkedin_ok else '❌'} LinkedIn {'Connected' if linkedin_ok else 'Disconnected'}",
        f"{'✅' if resume_ok else '❌'} Resume {'Loaded' if resume_ok else 'Not Found'}",
    ]
    return Panel(
        "\n".join(items),
        title=Text(" Status ", style="info"),
        border_style="border",
        box=MINIMAL,
    )


# ── Tables ───────────────────────────────────────────────────────────────────


def jobs_table(jobs: list[dict[str, Any]], max_rows: int = 10) -> Table:
    table = Table(
        title=Text(f"  Jobs ({len(jobs)} total)  ", style="primary"),
        box=HEAVY_EDGE,
        border_style="secondary",
        header_style="secondary.bold",
        show_lines=True,
        padding=(0, 1),
    )
    table.add_column("#", style="dim", width=3)
    table.add_column("Title", style="text", no_wrap=True)
    table.add_column("Company", style="text")
    table.add_column("Score", justify="right", width=6)
    table.add_column("Decision", width=10)

    for i, j in enumerate(jobs[:max_rows], 1):
        score = j.get("score", 0) or j.get("ranking", {}).get("score", 0)
        decision = j.get("decision", {}).get("decision", "PENDING")
        score_style = "score.high" if score >= 80 else "score.mid" if score >= 60 else "score.low"
        table.add_row(
            str(i),
            j.get("title", "—")[:50],
            j.get("company", "—")[:30],
            Text(f"{score:.0f}", style=score_style),
            Text(decision, style="accent" if decision == "APPLY" else "warning"),
        )
    return table


def score_breakdown_table(ranking: dict[str, Any]) -> Table:
    table = Table(
        box=MINIMAL,
        border_style="border",
        padding=(0, 1),
        show_edge=False,
    )
    table.add_column("Factor", style="dim")
    table.add_column("Score", justify="right")

    for key, label in [
        ("skill_match", "Skill Match"),
        ("resume_match", "Resume Match"),
        ("remote_match", "Remote"),
        ("experience_match", "Experience"),
        ("startup_match", "Startup Fit"),
        ("salary_match", "Salary"),
    ]:
        val = ranking.get(key, 0)
        style = "score.high" if val >= 80 else "score.mid" if val >= 60 else "score.low"
        table.add_row(label, Text(f"{val:.0f}/100", style=style))

    table.add_row(
        Text("───" * 6, style="dim"),
        Text("───" * 6, style="dim"),
    )
    total = ranking.get("score", 0)
    table.add_row(
        Text("Total", style="primary.bold"),
        Text(f"{total:.0f}/100", style="primary" if total >= 80 else "warning"),
    )
    return table


# ── Streaming text renderer ──────────────────────────────────────────────────


async def stream_text(
    text: str,
    delay: float = 0.008,
    style: str = "text",
    end: str = "",
) -> None:
    """Display text with typing animation, character by character."""
    for char in text:
        console.print(char, style=style, end="", highlight=False)
        sys.stdout.flush()
        await asyncio.sleep(delay)
    if end:
        console.print(end, style=style)


async def stream_markdown(
    text: str,
    delay: float = 0.004,
    code_theme: str = "monokai",
) -> None:
    """Display markdown line-by-line for a nice streaming effect."""
    lines = text.split("\n")
    buffer = ""
    for line in lines:
        buffer += line + "\n"
        if line.strip() == "":
            continue
        console.clear()
        md = Markdown(buffer, code_theme=code_theme)
        console.print(Panel(md, border_style="secondary", box=ROUNDED))
        await asyncio.sleep(delay * 10)


async def stream_generator(
    generator: AsyncGenerator[str, None],
    delay: float = 0.006,
) -> None:
    """Stream output from an async generator with typing animation."""
    async for chunk in generator:
        for char in chunk:
            console.print(char, style="text", end="", highlight=False)
            sys.stdout.flush()
            await asyncio.sleep(delay)


# ── Helpers ──────────────────────────────────────────────────────────────────


def rule(title: str = "") -> None:
    console.print(Rule(Text(title, style="dim"), style="border"))


def blank() -> None:
    console.print()


def header() -> None:
    console.print()
    console.print(
        Panel(
            Align.center(
                Text("🤖  AI JOB HUNTING ASSISTANT  🤖", style="bold primary"),
            ),
            box=HEAVY_EDGE,
            border_style="primary",
            padding=(1, 2),
        )
    )
    console.print()


def divider() -> None:
    console.print(Rule(style="border"))


def print_markdown(text: str, code_theme: str = "monokai") -> None:
    md = Markdown(text, code_theme=code_theme)
    console.print(md)


def print_json(data: Any, title: str = "") -> None:
    from rich.json import JSON
    json_str = JSON.from_data(data)
    if title:
        console.print(Panel(json_str, title=title, border_style="border", box=ROUNDED))
    else:
        console.print(json_str)
