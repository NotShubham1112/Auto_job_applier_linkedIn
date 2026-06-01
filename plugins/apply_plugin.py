from __future__ import annotations

from typing import AsyncGenerator

from plugins.base import Plugin, PluginContext
from ui.components import blank, console, make_progress, score_breakdown_table


class ApplyPlugin(Plugin):
    name = "apply"
    description = "Generate documents and apply to ranked jobs"
    aliases = ["a", "submit"]

    async def execute(self, args: str, context: PluginContext) -> AsyncGenerator[str, None]:
        apps = context.repo.get_all_applications(limit=50)

        pending = [a for a in apps if a.decision == "APPLY" and not a.resume_used]
        if not pending:
            pending = [a for a in apps if a.decision == "APPLY"]
            if not pending:
                yield "No pending applications found. Use `/jobhunt` to find and rank jobs first.\n"
                return

        yield f"📝 Found **{len(pending)}** pending applications\n\n"

        for idx, app in enumerate(pending[:10], 1):
            blank()
            yield f"### {idx}. {app.title} at {app.company}\n\n"
            yield f"**Score:** {app.score:.0f}/100  \n"
            yield f"**Decision:** {app.decision}  \n"

            if app.reasoning:
                yield f"> {app.reasoning}\n\n"

            act = await context.ask(f" Generate documents and record application for this job? [Y/n] > ")
            if act.lower().startswith("n"):
                yield "⏭️  Skipped.\n"
                continue

            yield "\n### 📄 Generating documents...\n\n"

            job_data = {
                "job_id": app.job_id,
                "title": app.title,
                "company": app.company,
                "description": app.description or "",
                "location": app.location or "",
                "platform": app.platform or "",
                "url": app.url or "",
            }
            ranking = {
                "score": app.score or 0,
                "confidence": app.confidence or 0,
            }

            try:
                resume_path = context.orchestrator.resume_agent.select_best_resume(job_data)
                summary = context.orchestrator.resume_agent.tailor_summary(job_data)
                cover = context.orchestrator.cover_letter_agent.generate(job_data)
                cl_path = context.orchestrator.cover_letter_agent.save(job_data, cover)

                yield f"**Resume:** {resume_path}\n\n"
                yield f"**Cover Letter:** {cl_path}\n\n"

                context.repo.update_application(
                    app.job_id,
                    resume_used=resume_path,
                    cover_letter_used=cl_path,
                )

                yield "✅ Application recorded!\n"
            except Exception as e:
                yield f"❌ Failed: {e}\n"

        yield "\n✅ Done! Use `/status` to see your updated stats.\n"
