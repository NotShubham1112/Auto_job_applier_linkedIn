from __future__ import annotations

from typing import AsyncGenerator

from plugins.base import Plugin, PluginContext
from ui.components import blank, console, jobs_table
from ui.styles import Palette


class JobsPlugin(Plugin):
    name = "jobs"
    description = "List recent job applications and their status"
    aliases = ["applications", "list"]

    async def execute(self, args: str, context: PluginContext) -> AsyncGenerator[str, None]:
        apps = context.repo.get_all_applications(limit=50)

        if not apps:
            yield "No applications yet. Use `/jobhunt` or `/search` to find jobs.\n"
            return

        # Build list for table
        jobs_data = []
        for a in apps:
            jobs_data.append({
                "title": a.title,
                "company": a.company,
                "score": a.score,
                "decision": {"decision": a.decision or "PENDING"},
                "ranking": {"score": a.score or 0},
            })

        blank()
        yield f"📋 Showing **{len(jobs_data)}** recent applications\n\n"
        blank()
        console.print(jobs_table(jobs_data, max_rows=20))
        blank()

        yield "Use `/jobs --detail N` to see a specific job, or `/status` for summary stats.\n"
