from __future__ import annotations

import logging
from typing import Any, AsyncGenerator

from rich.markdown import Markdown
from rich.panel import Panel
from rich.text import Text

from plugins.base import Plugin, PluginContext
from ui.components import (
    agent_panel,
    blank,
    console,
    divider,
    jobs_table,
    make_progress,
    make_spinner,
    rule,
    score_breakdown_table,
    stream_text,
)
from ui.styles import Palette

logger = logging.getLogger(__name__)

AGENT_SYSTEM_PROMPT = """You are an autonomous AI job hunting agent operating in a terminal.

You have these capabilities:
- Search for jobs across LinkedIn, Wellfound, YC Jobs, RemoteOK
- Rank jobs by match score using AI
- Generate tailored resumes and cover letters
- Decide whether to apply (APPLY/SKIP/REVIEW)
- Track all applications

The user will give you high-level instructions. Break them down into steps.

Available tools (describe what you want done):
1. search_jobs(keywords) — search across platforms
2. rank_jobs(jobs) — score jobs 0-100
3. decide_application(job) — APPLY/SKIP/REVIEW
4. generate_resume(job) — select + tailor resume
5. generate_cover_letter(job) — write + save cover letter
6. apply(job) — record application

Be proactive but always ask for confirmation before applying.
Explain your reasoning clearly.

Candidate profile:
{profile}

Current preferences: {preferences}
"""


class AgentPlugin(Plugin):
    """Autonomous mode — the agent takes initiative.

    Mode 3 of the system.
    """

    name = "agent"
    description = "Autonomous mode — agent searches, ranks, and applies with confirmation"
    aliases = ["auto", "autonomous"]

    async def execute(self, args: str, context: PluginContext) -> AsyncGenerator[str, None]:
        if not args:
            blank()
            console.print(agent_panel(
                "🤖 **Autonomous Agent Mode**\n\n"
                "I can autonomously search, rank, and apply to jobs.\n"
                "Just tell me what you're looking for:\n\n"
                "Examples:\n"
                "• \"Find remote AI engineer jobs and apply to top 5\"\n"
                "• \"Search for founding engineer roles at startups\"\n"
                "• \"Find jobs with salary above $150k\"\n"
            ))
            blank()
            args = await context.ask(" What should I do? > ")

        yield f"🤖 **Agent mode activated**\n\n"
        yield f"**Task:** {args}\n\n"

        # Parse intent using LLM
        plan = await self._plan(args, context)
        yield f"**Plan:**\n{plan}\n\n"

        if "search" in plan.lower() or "find" in plan.lower():
            async for token in self._execute_search(context):
                yield token
        else:
            yield "I'll execute this plan step by step. Implementing now...\n"

    async def _plan(self, task: str, context: PluginContext) -> str:
        messages = [
            {"role": "system", "content": AGENT_SYSTEM_PROMPT.format(
                profile=context.candidate_profile[:1000],
                preferences=context.recall("jobhunt_preferences", {}),
            )},
            {"role": "user", "content": f"Plan the steps for this task: {task}"},
        ]
        try:
            return context.groq.completion(messages, max_tokens=512)
        except Exception as e:
            return f"1. Search for jobs matching your criteria\n2. Rank them by relevance\n3. Ask you which to apply to\n4. Generate documents and apply"

    async def _execute_search(self, context: PluginContext) -> AsyncGenerator[str, None]:
        yield "🔍 **Searching for jobs...**\n\n"
        spinner = make_spinner("Searching all platforms...")
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
            yield "No new jobs found.\n"
            return

        yield f"✨ Found **{len(jobs)}** jobs\n\n"

        yield "📊 **Ranking jobs...**\n\n"
        ranked = []
        prog = make_progress("Ranking")
        with prog:
            task = prog.add_task("Scoring...", total=len(enriched))
            for j in enriched:
                try:
                    r = context.orchestrator.ranking_agent.rank(j, context.candidate_profile)
                    ranked.append((j, r))
                except Exception:
                    pass
                prog.update(task, advance=1)

        ranked.sort(key=lambda x: x[1].get("score", 0), reverse=True)
        yield f"✅ Ranked {len(ranked)} jobs\n\n"

        blank()
        console.print(jobs_table([
            {"title": j.get("title"), "company": j.get("company"),
             "score": r.get("score"), "decision": {"decision": "PENDING"},
             "ranking": r}
            for j, r in ranked[:15]
        ]))
        blank()

        n_str = await context.ask(" How many top matches should I process? [5] > ")
        try:
            n = max(1, min(int(n_str.strip()), len(ranked)))
        except (ValueError, AttributeError):
            n = 5

        for idx, (job, ranking) in enumerate(ranked[:n], 1):
            blank()
            divider()
            yield f"\n### #{idx}: {job.get('title')} at {job.get('company')}\n\n"
            yield f"**Score:** {ranking.get('score', 0):.0f}/100\n\n"

            score = ranking.get("score", 0)
            if score >= context.config.ranking.min_score_threshold:
                decision = context.orchestrator.application_agent.decide(job, ranking)
                dec = decision.get("decision", "SKIP")
                yield f"**AI Decision:** {dec}  \n"
                yield f"**Reason:** {decision.get('reasoning', '')}\n\n"

                if dec == "APPLY" and decision.get("confidence", 0) >= context.config.ranking.confidence_threshold:
                    act = await context.ask(f" Apply? [Y/n] > ")
                    if not act.lower().startswith("n"):
                        yield "📄 **Generating documents...**\n\n"
                        try:
                            rp = context.orchestrator.resume_agent.select_best_resume(job)
                            cl = context.orchestrator.cover_letter_agent.generate(job)
                            clp = context.orchestrator.cover_letter_agent.save(job, cl)
                            context.orchestrator.tracking_agent.record_application(
                                job=job, ranking=ranking, decision=decision,
                                resume_path=rp, cover_letter_path=clp,
                            )
                            yield "✅ **Applied!**\n"
                        except Exception as e:
                            yield f"❌ Failed: {e}\n"
                    else:
                        yield "⏭️  Skipped.\n"
                else:
                    yield "⏭️  AI recommends skipping or needs review.\n"
            else:
                yield f"⏭️  Score {score:.0f} below threshold.\n"

        yield "\n✅ **Agent task complete!**\n"
