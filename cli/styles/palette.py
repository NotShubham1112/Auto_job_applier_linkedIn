"""BROWORK theme palette — minimal aesthetic.

Centralizes colors used by every Textual/Rich component so the look
stays consistent across the boot sequence, panels, status bar, and
streaming output.

Design: extremely minimal. No borders, no box-drawing, no decorative
elements. Clean spacing and typography hierarchy only.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class OpenCodePalette:
    """Minimal palette — blue / white / red-rose on black.

    Only four colors are used in the entire UI:
      - Pure black background
      - White text
      - Blue (primary, brand)
      - Red rose (accent, alerts)

    One additional dim color for muted text hierarchy.
    """

    # Pure black surfaces
    background: str = "#000000"
    surface: str = "#000000"
    panel: str = "#000000"
    border: str = "#3b82f6"
    border_strong: str = "#3b82f6"

    # The three brand colors
    primary: str = "#3b82f6"
    accent: str = "#f43f5e"
    secondary: str = "#ffffff"

    # Semantic aliases
    success: str = "#3b82f6"
    info: str = "#3b82f6"
    warning: str = "#f43f5e"
    error: str = "#f43f5e"
    danger: str = "#f43f5e"

    # Text hierarchy
    text: str = "#ffffff"
    text_dim: str = "#666666"
    text_muted: str = "#444444"

    highlight: str = "#f43f5e"
    selection: str = "#3b82f6"

    user_color: str = "#ffffff"
    agent_color: str = "#3b82f6"
    command_color: str = "#f43f5e"

    spinner: str = "#3b82f6"
    progress_filled: str = "#3b82f6"
    progress_empty: str = "#ffffff"


PALETTE = OpenCodePalette()


# ── BROWORK product info ────────────────────────────────────────────────────

PRODUCT_NAME = "BROWORK"
PRODUCT_TAGLINE = "AI Engineering Workspace"
PRODUCT_VERSION = "1.0.0"


# ── Boot phases ────────────────────────────────────────────────────────────

BOOT_PHASES: list[tuple[str, str]] = [
    ("models", "Loading Models"),
    ("agents", "Loading Agents"),
    ("memory", "Loading Memory"),
    ("mcp", "Loading MCP Servers"),
    ("tools", "Loading Tools"),
]


# ── Rotating loading messages ─────────────────────────────────────────────

LOADING_MESSAGES: list[str] = [
    "Cooking solution...",
    "Hunting documentation...",
    "Reading codebase...",
    "Summoning agents...",
    "Consulting memory...",
    "Building execution plan...",
    "Reviewing architecture...",
    "Inspecting dependencies...",
    "Scanning repository...",
    "Generating implementation...",
    "Analyzing requirements...",
    "Composing prompt...",
    "Tracing context...",
    "Polishing output...",
]


# ── Spinner frames ────────────────────────────────────────────────────────

SPINNER_FRAMES: list[str] = ["\u280b", "\u2819", "\u2838", "\u2834",
                              "\u2826", "\u2827", "\u2807", "\u280f"]


# ── Progress bar characters ──────────────────────────────────────────────

PROGRESS_FRAMES: list[str] = [
    "[\u2591\u2591\u2591\u2591\u2591\u2591\u2591\u2591\u2591\u2591]",
    "[\u2588\u2591\u2591\u2591\u2591\u2591\u2591\u2591\u2591\u2591]",
    "[\u2588\u2588\u2591\u2591\u2591\u2591\u2591\u2591\u2591\u2591]",
    "[\u2588\u2588\u2588\u2591\u2591\u2591\u2591\u2591\u2591\u2591]",
    "[\u2588\u2588\u2588\u2588\u2591\u2591\u2591\u2591\u2591\u2591]",
    "[\u2588\u2588\u2588\u2588\u2588\u2591\u2591\u2591\u2591\u2591]",
    "[\u2588\u2588\u2588\u2588\u2588\u2588\u2591\u2591\u2591\u2591]",
    "[\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2591\u2591\u2591]",
    "[\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2591\u2591]",
    "[\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2591]",
    "[\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588]",
]


# ── Scan animation frames ──────────────────────────────────────────────────

SCAN_FRAMES: list[str] = [
    "\u2581\u2582\u2583\u2584\u2585\u2586\u2587\u2588",
    "\u2588\u2587\u2586\u2585\u2584\u2583\u2582\u2581",
]


# ── Matrix rain characters ─────────────────────────────────────────────────

MATRIX_CHARS: list[str] = [
    "0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
    "A", "B", "C", "D", "E", "F",
    "\u30a0", "\u30a1", "\u30a2", "\u30a3", "\u30a4",
    "\u30a5", "\u30a6", "\u30a7", "\u30a8", "\u30a9",
]
