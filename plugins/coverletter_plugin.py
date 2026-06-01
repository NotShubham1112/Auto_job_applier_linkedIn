from __future__ import annotations

from typing import AsyncGenerator

from rich.panel import Panel
from rich.text import Text

from plugins.base import Plugin, PluginContext
from ui.components import blank, console
from ui.styles import Palette


class CoverLetterPlugin(Plugin):
    name = "coverletter"
    description = "Generate and manage cover letters"
    aliases = ["cl", "letter", "cover"]

    async def execute(self, args: str, context: PluginContext) -> AsyncGenerator[str, None]:
        if not args:
            yield self._help()
            return

        parts = args.split(maxsplit=1)
        subcmd = parts[0].lower()

        if subcmd == "generate":
            job_id = parts[1] if len(parts) > 1 else ""
            async for chunk in self._generate_cover_letter(job_id, context):
                yield chunk
        elif subcmd == "show":
            job_id = parts[1] if len(parts) > 1 else ""
            yield self._show_cover_letter(job_id, context)
        elif subcmd == "list":
            yield self._list_cover_letters(context)
        else:
            yield self._help()

    async def _generate_cover_letter(
        self, job_id: str, context: PluginContext
    ) -> AsyncGenerator[str, None]:
        if not job_id:
            job_id = await context.ask(" Enter job ID to generate cover letter for > ")

        app = context.repo.get_application_by_job_id(job_id.strip())
        if not app:
            yield f"❌ No application found with job ID `{job_id}`\n"
            return

        job_data = {
            "job_id": app.job_id, "title": app.title, "company": app.company,
            "description": app.description or "", "location": app.location or "",
        }

        yield f"✍️  Generating cover letter for **{app.title}** at **{app.company}**...\n\n"
        try:
            cover = context.orchestrator.cover_letter_agent.generate(job_data)
            cl_path = context.orchestrator.cover_letter_agent.save(job_data, cover)
            yield "```\n" + cover + "\n```\n\n"
            yield f"✅ Saved to `{cl_path}`\n"
        except Exception as e:
            yield f"❌ Failed: {e}\n"

    def _show_cover_letter(self, job_id: str, context: PluginContext) -> str:
        if not job_id:
            return "Usage: `/coverletter show <job_id>`\n"
        docs = context.repo.get_documents_by_job_id(job_id)
        cls = [d for d in docs if d.doc_type == "cover_letter"]
        if not cls:
            return f"No cover letter found for job `{job_id}`\n"
        latest = cls[-1]
        return f"## Cover Letter\n\n```\n{latest.content}\n```\n"

    def _list_cover_letters(self, context: PluginContext) -> str:
        import glob
        import os
        gen_dir = context.config.resume.generated_resume_path
        files = sorted(glob.glob(os.path.join(gen_dir, "cover_letter_*.txt")))
        if not files:
            return "No generated cover letters found.\n"
        lines = ["## 📄 Generated Cover Letters\n\n"]
        for f in files[-20:]:
            name = os.path.basename(f)
            lines.append(f"  • `{name}`\n")
        lines.append(f"\n**Total:** {len(files)}\n")
        return "".join(lines)

    def _help(self) -> str:
        return (
            "Usage:\n"
            "  `/coverletter generate <job_id>` — generate cover letter\n"
            "  `/coverletter show <job_id>` — view existing cover letter\n"
            "  `/coverletter list` — list all generated cover letters\n"
        )
