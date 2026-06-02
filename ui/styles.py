from __future__ import annotations

from rich.style import Style
from rich.theme import Theme
from rich.color import Color

# ── BROWORK color palette (blue / white / red-rose on black) ─────────────
# Matches the Textual app's palette so any Rich-console output from
# existing plugins (tables, panels, etc.) stays consistent.
class Palette:
    PRIMARY = "#3b82f6"        # blue
    SECONDARY = "#ffffff"      # white
    ACCENT = "#f43f5e"         # red rose
    WARNING = "#f43f5e"
    SUCCESS = "#3b82f6"
    ERROR = "#f43f5e"
    INFO = "#3b82f6"
    MUTED = "#ffffff"
    DARK = "#000000"
    BG = "#000000"
    SURFACE = "#000000"
    TEXT = "#ffffff"
    TEXT_DIM = "#ffffff"
    LINK = "#3b82f6"
    HIGHLIGHT = "#f43f5e"

CUSTOM_THEME = Theme({
    "primary": Style(color=Palette.PRIMARY),
    "primary.bold": Style(color=Palette.PRIMARY, bold=True),
    "secondary": Style(color=Palette.SECONDARY),
    "secondary.bold": Style(color=Palette.SECONDARY, bold=True),
    "accent": Style(color=Palette.ACCENT),
    "accent.bold": Style(color=Palette.ACCENT, bold=True),
    "success": Style(color=Palette.SUCCESS),
    "success.bold": Style(color=Palette.SUCCESS, bold=True),
    "warning": Style(color=Palette.WARNING),
    "warning.bold": Style(color=Palette.WARNING, bold=True),
    "error": Style(color=Palette.ERROR),
    "error.bold": Style(color=Palette.ERROR, bold=True),
    "info": Style(color=Palette.INFO),
    "info.bold": Style(color=Palette.INFO, bold=True),
    "muted": Style(color=Palette.MUTED),
    "text": Style(color=Palette.TEXT),
    "text.dim": Style(color=Palette.TEXT_DIM),
    "dim": Style(color=Palette.TEXT_DIM),
    "link": Style(color=Palette.LINK, underline=True),
    "highlight": Style(color=Palette.HIGHLIGHT),
    "agent": Style(color=Palette.PRIMARY, bold=True),
    "user": Style(color="#ffffff", bold=True),
    "command": Style(color=Palette.ACCENT, bold=True),
    "score.high": Style(color=Palette.PRIMARY, bold=True),
    "score.mid": Style(color=Palette.ACCENT),
    "score.low": Style(color=Palette.ACCENT),
    "border": Style(color=Palette.PRIMARY, dim=True),
})

HEADER = """
╭───────────────────────────────────────╮
│       🤖  AI JOB HUNTING ASSISTANT     │
╰───────────────────────────────────────╯
"""

STATUS_TEMPLATE = """
 Status:
 {groq} Groq Connected
 {linkedin} LinkedIn Connected
 {resume} Resume Loaded
 """
