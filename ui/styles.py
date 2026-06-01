from __future__ import annotations

from rich.style import Style
from rich.theme import Theme
from rich.color import Color

# ── Color palette ──────────────────────────────────────────────────────────
class Palette:
    PRIMARY = "#00FFAA"
    SECONDARY = "#00AAFF"
    ACCENT = "#FF6B6B"
    WARNING = "#FFD93D"
    SUCCESS = "#6BCB77"
    ERROR = "#FF4757"
    INFO = "#5352ED"
    MUTED = "#636E72"
    DARK = "#2D3436"
    BG = "#1A1A2E"
    SURFACE = "#16213E"
    TEXT = "#EAEAEA"
    TEXT_DIM = "#A0A0B0"
    LINK = "#74B9FF"
    HIGHLIGHT = "#FFEAA7"

CUSTOM_THEME = Theme({
    "primary": Style(color=Palette.PRIMARY, bold=True),
    "secondary": Style(color=Palette.SECONDARY),
    "accent": Style(color=Palette.ACCENT, bold=True),
    "success": Style(color=Palette.SUCCESS),
    "warning": Style(color=Palette.WARNING),
    "error": Style(color=Palette.ERROR, bold=True),
    "info": Style(color=Palette.INFO),
    "muted": Style(color=Palette.MUTED),
    "text": Style(color=Palette.TEXT),
    "dim": Style(color=Palette.TEXT_DIM),
    "link": Style(color=Palette.LINK, underline=True),
    "highlight": Style(color=Palette.HIGHLIGHT),
    "header": Style(color=Palette.PRIMARY, bold=True),
    "agent": Style(color=Palette.SECONDARY, bold=True),
    "user": Style(color=Palette.ACCENT, bold=True),
    "command": Style(color=Palette.WARNING, bold=True),
    "score_high": Style(color=Palette.SUCCESS, bold=True),
    "score_mid": Style(color=Palette.WARNING),
    "score_low": Style(color=Palette.ERROR),
    "border": Style(color=Palette.MUTED, dim=True),
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
