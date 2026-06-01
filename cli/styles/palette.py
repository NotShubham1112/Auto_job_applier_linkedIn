"""BROWORK theme palette — OpenCode / Vim / Warp inspired colors.

Centralizes colors used by every Textual/Rich component so the look
stays consistent across the boot sequence, panels, status bar, and
streaming output.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class OpenCodePalette:
    """OpenCode-inspired terminal palette.

    Mirrors the warm-on-dark scheme used by OpenCode, Claude Code,
    Gemini CLI, and Warp Terminal AI panels.
    """

    background: str = "#0a0a0a"
    surface: str = "#141414"
    panel: str = "#1a1a1a"
    border: str = "#2a2a2a"
    border_strong: str = "#3a3a3a"

    accent: str = "#f4b183"
    primary: str = "#f4b183"
    secondary: str = "#58a6ff"
    success: str = "#7ee787"
    info: str = "#58a6ff"
    warning: str = "#e3b341"
    error: str = "#ff6b6b"
    danger: str = "#f85149"

    text: str = "#e6e6e6"
    text_dim: str = "#9a9a9a"
    text_muted: str = "#6a6a6a"

    highlight: str = "#f4b183"
    selection: str = "#2a2a2a"

    user_color: str = "#f4b183"
    agent_color: str = "#7ee787"
    command_color: str = "#e3b341"

    spinner: str = "#f4b183"
    progress_filled: str = "#f4b183"
    progress_empty: str = "#2a2a2a"


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


# ── Rotating loading messages (OpenCode style) ─────────────────────────────

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


# ── Spinner frames (opencode-style) ────────────────────────────────────────

SPINNER_FRAMES: list[str] = ["\u280b", "\u2819", "\u2838", "\u2834",
                              "\u2826", "\u2827", "\u2807", "\u280f"]


# ── Progress bar characters (opencode-style) ──────────────────────────────

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


# ── Box-drawing characters for custom borders ─────────────────────────────

ROUNDED_BORDER: dict[str, str] = {
    "top": "\u256d",
    "bottom": "\u256e",
    "left": "\u2502",
    "right": "\u2502",
    "top_left": "\u256d",
    "top_right": "\u256e",
    "bottom_left": "\u2570",
    "bottom_right": "\u256f",
}


HEAVY_BORDER: dict[str, str] = {
    "top": "\u2501",
    "bottom": "\u2501",
    "left": "\u2503",
    "right": "\u2503",
    "top_left": "\u250f",
    "top_right": "\u2513",
    "bottom_left": "\u2517",
    "bottom_right": "\u251b",
}
