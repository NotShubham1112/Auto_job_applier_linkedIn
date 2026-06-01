"""Catalog of all slash commands available in BROWORK.

Combines the existing plugin commands (registered at runtime) with
the OpenCode-style developer-focused commands (/research, /build,
/fix, /review, /architect, /debug, /ship).
"""

from __future__ import annotations

from typing import Callable, Optional

from cli.widgets.command_palette import PaletteCommand


# Categories used in the command palette and help screen
CAT_GENERAL = "General"
CAT_JOBHUNT = "Job Hunting"
CAT_RESUME = "Resume & Documents"
CAT_HISTORY = "History & Memory"
CAT_DEVELOPER = "Developer"


def build_static_commands() -> list[PaletteCommand]:
    """Return the OpenCode-style commands that always exist.

    These complement the plugin-discovered commands and are useful
    even when the plugin system isn't loaded.
    """
    return [
        # General
        PaletteCommand(
            name="new",
            description="Start a new session",
            aliases=[],
            category=CAT_GENERAL,
        ),
        PaletteCommand(
            name="help",
            description="Show help and command list",
            aliases=["h", "?"],
            category=CAT_GENERAL,
        ),
        PaletteCommand(
            name="clear",
            description="Clear the chat screen",
            aliases=["c"],
            category=CAT_GENERAL,
        ),
        PaletteCommand(
            name="share",
            description="Share this session (export transcript)",
            aliases=[],
            category=CAT_GENERAL,
        ),
        PaletteCommand(
            name="exit",
            description="Quit BROWORK",
            aliases=["quit", "q"],
            category=CAT_GENERAL,
        ),
        # Models / agents / memory
        PaletteCommand(
            name="models",
            description="List available models",
            aliases=["model"],
            category=CAT_GENERAL,
        ),
        PaletteCommand(
            name="agents",
            description="List available agents",
            aliases=["agent"],
            category=CAT_GENERAL,
        ),
        PaletteCommand(
            name="memory",
            description="Show conversation memory",
            aliases=[],
            category=CAT_HISTORY,
        ),
        PaletteCommand(
            name="history",
            description="Show session history",
            aliases=[],
            category=CAT_HISTORY,
        ),
        PaletteCommand(
            name="tasks",
            description="Show background tasks",
            aliases=[],
            category=CAT_HISTORY,
        ),
        PaletteCommand(
            name="settings",
            description="Open settings panel",
            aliases=["config"],
            category=CAT_GENERAL,
        ),
        # Job hunting
        PaletteCommand(
            name="jobhunt",
            description="Run the full job hunt workflow",
            aliases=["hunt"],
            category=CAT_JOBHUNT,
        ),
        PaletteCommand(
            name="search",
            description="Search for new jobs",
            aliases=["find"],
            category=CAT_JOBHUNT,
        ),
        PaletteCommand(
            name="status",
            description="Show your application statistics",
            aliases=["stats"],
            category=CAT_JOBHUNT,
        ),
        PaletteCommand(
            name="jobs",
            description="List discovered jobs",
            aliases=[],
            category=CAT_JOBHUNT,
        ),
        PaletteCommand(
            name="apply",
            description="Apply to a specific job",
            aliases=[],
            category=CAT_JOBHUNT,
        ),
        PaletteCommand(
            name="interviews",
            description="Show scheduled interviews",
            aliases=[],
            category=CAT_JOBHUNT,
        ),
        # Resume / cover
        PaletteCommand(
            name="resume",
            description="Generate / tailor resume",
            aliases=[],
            category=CAT_RESUME,
        ),
        PaletteCommand(
            name="coverletter",
            description="Write a cover letter",
            aliases=["cover"],
            category=CAT_RESUME,
        ),
        PaletteCommand(
            name="chat",
            description="General career chat mode",
            aliases=["ask", "advice"],
            category=CAT_RESUME,
        ),
        # Developer-focused
        PaletteCommand(
            name="research",
            description="Research a topic (LLM deep-dive)",
            aliases=[],
            category=CAT_DEVELOPER,
        ),
        PaletteCommand(
            name="build",
            description="Build a plan / scaffold a project",
            aliases=[],
            category=CAT_DEVELOPER,
        ),
        PaletteCommand(
            name="fix",
            description="Diagnose and fix a problem",
            aliases=[],
            category=CAT_DEVELOPER,
        ),
        PaletteCommand(
            name="review",
            description="Review code or decisions",
            aliases=[],
            category=CAT_DEVELOPER,
        ),
        PaletteCommand(
            name="architect",
            description="Design a system architecture",
            aliases=["arch"],
            category=CAT_DEVELOPER,
        ),
        PaletteCommand(
            name="debug",
            description="Debug a runtime issue",
            aliases=[],
            category=CAT_DEVELOPER,
        ),
        PaletteCommand(
            name="ship",
            description="Ship a feature / finalize deliverables",
            aliases=[],
            category=CAT_DEVELOPER,
        ),
    ]


def commands_to_palette(
    static_cmds: list[PaletteCommand],
    plugin_cmds: list[tuple[str, list[str], str]],
) -> list[PaletteCommand]:
    """Convert a list of plugin commands into PaletteCommand objects.

    plugin_cmds is a list of (name, aliases, description) tuples —
    the shape returned by ``PluginRegistry.commands_list()``.
    """
    result: list[PaletteCommand] = list(static_cmds)
    existing = {c.name for c in static_cmds}
    for name, aliases, desc in plugin_cmds:
        clean = name.lstrip("/")
        if clean in existing:
            continue
        result.append(PaletteCommand(
            name=clean,
            description=desc or "Plugin command",
            aliases=[a.lstrip("/") for a in aliases.split(",") if a.strip()],
            category="Plugin",
        ))
        existing.add(clean)
    return result
