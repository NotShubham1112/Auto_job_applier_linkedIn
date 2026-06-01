from __future__ import annotations

from typing import AsyncGenerator

from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from plugins.base import Plugin, PluginContext
from ui.components import blank, console
from ui.styles import Palette


class ResumePlugin(Plugin):
    name = "resume"
    description = "Manage resumes — view, select, tailor"
    aliases = ["cv"]

    async def execute(self, args: str, context: PluginContext) -> AsyncGenerator[str, None]:
        if not args:
            yield self._show_resumes(context)
            return

        parts = args.split(maxsplit=1)
        subcmd = parts[0].lower()
        subargs = parts[1] if len(parts) > 1 else ""

        if subcmd in ("show", "view", "list"):
            yield self._show_resumes(context)
        elif subcmd in ("select", "use"):
            yield await self._select_resume(subargs, context)
        elif subcmd == "tailor":
            yield await self._tailor_resume(subargs, context)
        elif subcmd == "profile":
            yield self._show_profile(context)
        else:
            yield f"Unknown subcommand: `{subcmd}`\n\n"
            yield self._help()

    def _show_resumes(self, context: PluginContext) -> str:
        lines = ["## 📄 Available Resumes\n\n"]

        import glob as g
        import os
        resume_dir = context.config.resume.resumes_dir
        pdfs = g.glob(os.path.join(resume_dir, "*.pdf"))
        txts = g.glob(os.path.join(resume_dir, "*.txt"))
        files = sorted(pdfs + txts)

        if not files:
            lines.append("No resume files found.\n")
        else:
            for f in files:
                lines.append(f"  • `{os.path.basename(f)}`\n")

        default = context.config.resume.default_resume_path
        lines.append(f"\n**Default:** {default}\n")
        lines.append("\nUse `/resume select <filename>` to change.\n")
        return "".join(lines)

    async def _select_resume(self, filename: str, context: PluginContext) -> str:
        if not filename:
            return "Usage: `/resume select <filename>`\n"
        import os
        path = os.path.join(context.config.resume.resumes_dir, filename)
        if not os.path.exists(path):
            return f"❌ Resume `{filename}` not found in `{context.config.resume.resumes_dir}`\n"
        context.config.resume.default_resume_path = path
        return f"✅ Default resume set to `{path}`\n"

    async def _tailor_resume(self, job_id: str, context: PluginContext) -> str:
        if not job_id:
            return "Usage: `/resume tailor <job_id>`\n"
        app = context.repo.get_application_by_job_id(job_id)
        if not app:
            return f"❌ No application found with job ID `{job_id}`\n"
        job_data = {
            "job_id": app.job_id, "title": app.title, "company": app.company,
            "description": app.description or "", "location": app.location or "",
        }
        try:
            summary = context.orchestrator.resume_agent.tailor_summary(job_data)
            return f"✅ Tailored summary generated:\n\n> {summary}\n"
        except Exception as e:
            return f"❌ Failed: {e}\n"

    def _show_profile(self, context: PluginContext) -> str:
        profile = context.candidate_profile
        if not profile:
            return "No candidate profile loaded.\n"
        preview = profile[:2000]
        return f"## 👤 Candidate Profile\n\n```markdown\n{preview}\n```\n"

    def _help(self) -> str:
        return (
            "Usage:\n"
            "  `/resume` — list resumes\n"
            "  `/resume show` — show all resumes\n"
            "  `/resume select <filename>` — set default resume\n"
            "  `/resume tailor <job_id>` — tailor summary for a job\n"
            "  `/resume profile` — view candidate profile\n"
        )
