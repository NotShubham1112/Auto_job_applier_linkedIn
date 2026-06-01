from __future__ import annotations

from typing import AsyncGenerator

from rich.table import Table
from rich.text import Text

from plugins.base import Plugin, PluginContext
from ui.components import blank, console
from ui.styles import Palette


class HistoryPlugin(Plugin):
    name = "history"
    description = "Show conversation and application history"
    aliases = ["log", "recent"]

    async def execute(self, args: str, context: PluginContext) -> AsyncGenerator[str, None]:
        apps = context.repo.get_all_applications(limit=30)

        if not apps:
            yield "No application history yet.\n"
            return

        reports = context.repo.get_recent_reports(days=30)

        blank()
        yield f"## 📜 Application History\n\n"
        yield f"**Total records:** {len(apps)}\n\n"

        table = Table(
            box=None,
            padding=(0, 2),
        )
        table.add_column("Date", style="dim", width=10)
        table.add_column("Company", style="text", width=25)
        table.add_column("Role", style="text", width=30)
        table.add_column("Score", justify="right", width=6)
        table.add_column("Status", width=12)

        for a in apps[:20]:
            date_str = a.date_applied.strftime("%b %d") if a.date_applied else "—"
            status = a.status or a.decision or "—"
            score = a.score or 0
            score_str = Text(f"{score:.0f}", style="score_high" if score >= 80 else "score_mid" if score >= 60 else "score_low")
            table.add_row(date_str, a.company[:24], a.title[:29], score_str, str(status)[:11])

        console.print(table)
        blank()

        if reports:
            yield "### 📊 Daily Reports\n\n"
            for r in reports[:7]:
                yield f"  • **{r.report_date}**: {r.total_applied} applied, {r.total_skipped} skipped, avg {r.avg_score:.0f}/100\n"

        yield "\nUse `/jobs` to see more, or `/status` for summary statistics.\n"
