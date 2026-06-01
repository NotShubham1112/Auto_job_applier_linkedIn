from __future__ import annotations

from typing import AsyncGenerator

from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from plugins.base import Plugin, PluginContext
from ui.components import blank, console, status_panel
from ui.styles import Palette


class StatusPlugin(Plugin):
    name = "status"
    description = "Show current system status and application statistics"
    aliases = ["stats", "dashboard"]

    async def execute(self, args: str, context: PluginContext) -> AsyncGenerator[str, None]:
        stats = context.repo.get_dashboard_stats()

        blank()
        # Status checks
        groq_ok = bool(context.config.ai.groq_api_key)
        linkedin_ok = True  # Assume connected
        resume_ok = bool(context.candidate_profile)

        console.print(status_panel(groq_ok, linkedin_ok, resume_ok))
        blank()

        # Stats table
        table = Table(title=Text(" Application Statistics ", style="bold primary"), box=None, padding=(0, 2))
        table.add_column("Metric", style="dim")
        table.add_column("Value", justify="right", style="text")

        total = stats.get("total_applications", 0)
        today = stats.get("applications_today", 0)
        rate = stats.get("response_rate", 0)
        score_dist = stats.get("score_distribution", {})
        status_counts = stats.get("status_counts", {})

        table.add_row("Total Applications", str(total))
        table.add_row("Today", str(today))
        table.add_row("Response Rate", f"{rate:.1f}%")
        table.add_row("Avg Score", f"{score_dist.get('avg_score', 0):.1f}")

        for status, count in sorted(status_counts.items()):
            table.add_row(f"  ├ {status}", str(count))

        blank()
        console.print(table)
        blank()

        yield f"📊 **{total}** total applications | **{today}** today\n"
        yield f"📈 **{rate:.1f}%** response rate\n"
