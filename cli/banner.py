"""BROWORK boot sequence — ASCII logo + animated initialization.

The boot screen shows the BROWORK logo, then a list of subsystems
loading in sequence, then "Ready."

This is purely a render function — animation is driven by the caller
(typically the BootScreen widget) so the visual sequence can be
timed and orchestrated from one place.
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
    """Return (label, css_class, mark) for a boot phase by index.

    The returned tuple is suitable for direct use by a ListView / Static:
      - label: the text to display
      - css_class: 'pending' | 'active' | 'done'
      - mark: the leading character (○ ● ✓)
    """
    if index < 0 or index >= len(BOOT_PHASES):
        return "", "pending", " "

    phase_id, phase_label = BOOT_PHASES[index]
    return phase_label, "pending", "[ ]"


def boot_phase_done(phase_id: str) -> tuple[str, str, str]:
    """Return the rendered state for a phase that's been completed."""
    for pid, label in BOOT_PHASES:
        if pid == phase_id:
            return label, "done", "[+]"
    return phase_id, "done", "[+]"


def boot_phase_active(phase_id: str) -> tuple[str, str, str]:
    """Return the rendered state for a phase that's currently loading."""
    for pid, label in BOOT_PHASES:
        if pid == phase_id:
            return label, "active", "[~]"
    return phase_id, "active", "[~]"


# ── Welcome screen content ────────────────────────────────────────────────


def render_welcome_panel() -> str:
    """Return the welcome panel content shown after the boot completes."""
    return (
        f"[bold {PALETTE.primary}]  {PRODUCT_NAME} CLI[/]\n"
        f"\n"
        f"  [{PALETTE.command_color}]/{'new':<10}[/] [dim]Create Session[/]\n"
        f"  [{PALETTE.command_color}]/{'agents':<10}[/] [dim]List Agents[/]\n"
        f"  [{PALETTE.command_color}]/{'models':<10}[/] [dim]List Models[/]\n"
        f"  [{PALETTE.command_color}]/{'memory':<10}[/] [dim]Show Memory[/]\n"
        f"  [{PALETTE.command_color}]/{'settings':<10}[/] [dim]Settings[/]\n"
        f"  [{PALETTE.command_color}]/{'help':<10}[/] [dim]Show Help[/]\n"
        f"\n"
        f"  [{PALETTE.text_dim}]press [bold]ctrl+x[/] for command palette  "
        f"  [bold]ctrl+c[/] to exit[/]"
    )


# ── Legacy rich-console boot (used when running outside Textual) ────────


def print_boot_console(console=None) -> None:
    """Print the boot sequence using rich.Console directly.

    Useful for the pre-Textual fallback (e.g. when Textual fails to
    initialize, or when running headless). Animation is simulated with
    a small sleep so the visual flow is preserved.
    """
    import time

    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text

    con = console or Console()

    con.print()
    con.print(
        Panel(
            Text(BROWORK_LOGO, style=f"bold {PALETTE.primary}"),
            border_style=PALETTE.primary,
            padding=(0, 2),
        )
    )
    con.print(f"  [{PALETTE.text_dim}]{PRODUCT_TAGLINE}[/]")
    con.print(f"  [{PALETTE.text_muted}]v{PRODUCT_VERSION}[/]")
    con.print()

    for phase_id, label in BOOT_PHASES:
        time.sleep(0.12)
        con.print(f"  [{PALETTE.success}][\u2713][/] {label}")

    con.print()
    con.print(f"  [{PALETTE.success}]Ready.[/]")
    con.print()
