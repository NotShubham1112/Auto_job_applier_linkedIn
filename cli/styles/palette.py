"""BROWORK theme palette — OpenCode / Vim / Warp inspired colors.

Centralizes colors used by every Textual/Rich component so the look
stays consistent across the boot sequence, panels, status bar, and
streaming output.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class OpenCodePalette:
    """Clean professional palette — blue / white / red-rose on black.

    Only four colors are used in the entire UI:
      - Pure black background
      - White text and panels
      - Blue (primary, focus, brand)
      - Red rose (accent, alerts, highlights)

    No intermediate grays, no dim text — everything is high contrast
    so it renders identically across every terminal.
    """

    # Pure black surfaces
    background: str = "#000000"
    surface: str = "#000000"
    panel: str = "#000000"
    border: str = "#3b82f6"
    border_strong: str = "#3b82f6"

    # The three brand colors
    primary: str = "#3b82f6"        # blue
    accent: str = "#f43f5e"         # red rose
    secondary: str = "#ffffff"      # white

    # Semantic aliases (still in the 3-color family)
    success: str = "#3b82f6"        # blue
    info: str = "#3b82f6"           # blue
    warning: str = "#f43f5e"        # red rose
    error: str = "#f43f5e"          # red rose
    danger: str = "#f43f5e"         # red rose

    # Text — all white, no dim variants
    text: str = "#ffffff"
    text_dim: str = "#ffffff"
    text_muted: str = "#ffffff"

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
