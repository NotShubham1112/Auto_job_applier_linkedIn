from __future__ import annotations

from typing import AsyncGenerator

from rich.table import Table
from rich.text import Text

from config.settings import ApplicationStatus
from plugins.base import Plugin, PluginContext
from ui.components import blank, console
from ui.styles import Palette


class InterviewsPlugin(Plugin):
    name = "interviews"
    description = "Track interview invitations and status"
    aliases = ["interview", "offers"]

    async def execute(self, args: str, context: PluginContext) -> AsyncGenerator[str, None]:
        interviews = context.repo.get_applications_by_status(ApplicationStatus.INTERVIEW)
        offers = context.repo.get_applications_by_status(ApplicationStatus.OFFER)
        rejected = context.repo.get_applications_by_status(ApplicationStatus.REJECTED)

        blank()

        if not (interviews or offers or rejected):
            yield "No tracked responses yet. Keep applying!\n"
            return

        table = Table(
            title=Text(" Response Tracking ", style="bold primary"),
            box=None,
            padding=(0, 2),
        )
        table.add_column("Type", style="dim", width=14)
        table.add_column("Company", style="text")
        table.add_column("Role", style="text")
        table.add_column("Date", style="dim")

        for app in interviews:
            table.add_row(
                Text("🎙️ Interview", style="info"),
                app.company, app.title,
                app.date_applied.strftime("%b %d") if app.date_applied else "—",
            )
        for app in offers:
            table.add_row(
                Text("🎉 Offer", style="success"),
                app.company, app.title,
                app.date_applied.strftime("%b %d") if app.date_applied else "—",
            )
        for app in rejected:
            table.add_row(
                Text("❌ Rejected", style="error"),
                app.company, app.title,
                app.date_applied.strftime("%b %d") if app.date_applied else "—",
            )

        console.print(table)
        blank()

        yield f"📊 **{len(interviews)}** interviews | **{len(offers)}** offers | **{len(rejected)}** rejections\n"
        yield "\nUse `/status` for full statistics.\n"
