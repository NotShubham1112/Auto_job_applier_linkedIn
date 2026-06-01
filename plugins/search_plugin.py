from __future__ import annotations

from typing import AsyncGenerator

from plugins.base import Plugin, PluginContext
from ui.components import blank, console, jobs_table, make_spinner


class SearchPlugin(Plugin):
    """Quick job search without the full workflow."""

    name = "search"
    description = "Quick search for jobs across all platforms"
    aliases = ["s", "find"]

    async def execute(self, args: str, context: PluginContext) -> AsyncGenerator[str, None]:
        if args:
            context.config.search.search_terms = [args]

        term = context.config.search.search_terms[0]
        yield f"🔍 Searching for **{term}**...\n\n"

        spinner = make_spinner(f"Searching {', '.join(p.value for p in context.config.search.platforms)}...")
        with spinner:
            try:
                jobs = context.orchestrator.search_agent.search()
                enriched = []
                for j in jobs:
                    try:
                        enriched.append(context.orchestrator.search_agent.enrich_job(j))
                    except Exception:
                        enriched.append(j)
            except Exception as e:
                yield f"❌ Search failed: {e}\n"
                return

        if not jobs:
            yield "No jobs found. Try different search terms.\n"
            return

        yield f"✨ Found **{len(jobs)}** jobs\n\n"

        ranked = []
        for j in enriched:
            try:
                ranking = context.orchestrator.ranking_agent.rank(j, context.candidate_profile)
                ranked.append((j, ranking))
            except Exception:
                pass

        ranked.sort(key=lambda x: x[1].get("score", 0), reverse=True)

        blank()
        console.print(jobs_table([
            {"title": j.get("title"), "company": j.get("company"),
             "score": r.get("score"), "decision": {"decision": "PENDING"},
             "ranking": r}
            for j, r in ranked[:20]
        ]))
        blank()

        if ranked:
            yield f"Top score: **{ranked[0][1].get('score', 0):.0f}/100**\n"
            yield f"Use `/apply` to apply, or `/jobhunt` for the full interactive workflow.\n"
