"""BROWORK boot sequence — logo + boot phase rendering.

Pure render functions — animation is driven by the caller (BootScreen).
No decorative elements, no panel wrapping.
"""

from __future__ import annotations

from cli.styles.palette import (
    BOOT_PHASES,
    PALETTE,
    PRODUCT_NAME,
    PRODUCT_TAGLINE,
    PRODUCT_VERSION,
)


# ── ASCII Logo ──────────────────────────────────────────────────────────────

BROWORK_LOGO: str = r"""
██████╗ ██████╗  ██████╗ ██╗    ██╗ ██████╗ ██████╗ ██╗  ██╗
██╔══██╗██╔══██╗██╔═══██╗██║    ██║██╔═══██╗██╔══██╗██║ ██╔╝
██████╔╝██████╔╝██║   ██║██║ █╗ ██║██║   ██║██████╔╝█████╔╝
██╔══██╗██╔══██╗██║   ██║██║███╗██║██║   ██║██╔══██╗██╔═██╗
██████╔╝██║  ██║╚██████╔╝╚███╔███╔╝╚██████╔╝██║  ██║██║  ██╗
╚═════╝ ╚═╝  ╚═╝ ╚═════╝  ╚══╝╚══╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝
"""


def render_logo() -> str:
    """Return the BROWORK logo with tagline + version underneath."""
    lines = [BROWORK_LOGO.rstrip("\n")]
    lines.append("")
    lines.append(f"{PRODUCT_TAGLINE}")
    lines.append(f"v{PRODUCT_VERSION}")
    return "\n".join(lines)


# ── Boot phase labels ──────────────────────────────────────────────────────


def render_boot_phase(index: int) -> tuple[str, str, str]:
    """Return (label, css_class, mark) for a boot phase by index."""
    if index < 0 or index >= len(BOOT_PHASES):
        return "", "pending", " "
    phase_id, phase_label = BOOT_PHASES[index]
    return phase_label, "pending", "\u00b7"


def boot_phase_done(phase_id: str) -> tuple[str, str, str]:
    """Return the rendered state for a completed phase."""
    for pid, label in BOOT_PHASES:
        if pid == phase_id:
            return label, "done", "\u25cf"
    return phase_id, "done", "\u25cf"


def boot_phase_active(phase_id: str) -> tuple[str, str, str]:
    """Return the rendered state for an active phase."""
    for pid, label in BOOT_PHASES:
        if pid == phase_id:
            return label, "active", "\u25cb"
    return phase_id, "active", "\u25cb"


# ── Welcome screen content ────────────────────────────────────────────────


def render_welcome_panel() -> str:
    """Return the welcome panel content shown after the boot completes."""
    return (
        f"[bold {PALETTE.primary}]  {PRODUCT_NAME}[/]\n"
        f"\n"
        f"  [{PALETTE.command_color}]/{'new':<10}[/] [{PALETTE.text_dim}]Create Session[/]\n"
        f"  [{PALETTE.command_color}]/{'agents':<10}[/] [{PALETTE.text_dim}]List Agents[/]\n"
        f"  [{PALETTE.command_color}]/{'models':<10}[/] [{PALETTE.text_dim}]List Models[/]\n"
        f"  [{PALETTE.command_color}]/{'memory':<10}[/] [{PALETTE.text_dim}]Show Memory[/]\n"
        f"  [{PALETTE.command_color}]/{'settings':<10}[/] [{PALETTE.text_dim}]Settings[/]\n"
        f"  [{PALETTE.command_color}]/{'help':<10}[/] [{PALETTE.text_dim}]Show Help[/]\n"
        f"\n"
        f"  [{PALETTE.text_muted}]press [bold]{PALETTE.text_dim}ctrl+x[/] for command palette  "
        f"  [bold]{PALETTE.text_dim}ctrl+c[/] to exit[/]"
    )


# ── Legacy rich-console boot ─────────────────────────────────────────────


def print_boot_console(console=None) -> None:
    """Print the boot sequence using rich.Console directly.

    Fallback for when Textual fails to initialize.
    """
    import time

    from rich.console import Console

    con = console or Console()

    con.print()
    con.print(f"  [bold {PALETTE.primary}]{BROWORK_LOGO.rstrip(chr(10))}[/]")
    con.print()
    con.print(f"  [{PALETTE.text_dim}]{PRODUCT_TAGLINE}[/]")
    con.print(f"  [{PALETTE.text_muted}]v{PRODUCT_VERSION}[/]")
    con.print()

    for phase_id, label in BOOT_PHASES:
        time.sleep(0.12)
        con.print(f"  [{PALETTE.primary}]\u25cf[/] {label}")

    con.print()
    con.print(f"  [{PALETTE.accent}]Ready.[/]")
    con.print()
