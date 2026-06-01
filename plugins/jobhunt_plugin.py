from __future__ import annotations

import json
import logging
from typing import Any, AsyncGenerator

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
    stream_generator,
)
from ui.styles import Palette

logger = logging.getLogger(__name__)

JOBHUNT_PREF_KEY = "jobhunt_preferences"


class JobHuntPlugin(Plugin):
    """Interactive job search and application workflow.

    Mode 1 of the system — walks the user through preferences,
    searches across platforms, ranks results, and handles applications.
    """

    name = "jobhunt"
    description = "Start an interactive job search and application workflow"
    aliases = ["jh", "hunt"]

    async def execute(self, args: str, context: PluginContext) -> AsyncGenerator[str, None]:
        profile_name = context.config.personal.first_name or "there"
        prefs = context.recall(JOBHUNT_PREF_KEY, {})

        blank()
        console.print(agent_panel(
            f"Hello **{profile_name}**! Let's find you some great opportunities.\n\n"
            "I can search **LinkedIn**, **Wellfound**, **YC Jobs**, and **RemoteOK** "
            "to find roles that match your profile.\n"
        ))
        blank()

        # ── Gather preferences (skip if already set) ──
        if not prefs:
            prefs = await self._gather_preferences(context)
            context.store(JOBHUNT_PREF_KEY, prefs)
            yield "✅ Preferences saved! You can change them anytime with `/settings`\n\n"
        else:
            yield f"📋 Using saved preferences:\n"
            yield f"   • Role: {prefs.get('role', 'Any')}\n"
            yield f"   • Remote: {prefs.get('remote', 'Yes')}\n"
            yield f"   • Salary: {prefs.get('salary', 'Not specified')}\n"
            yield f"   • Experience: {prefs.get('experience', '0')} years\n\n"

        # ── Confirm / adjust ──
        blank()
        answer = await context.ask(" Shall I search with these preferences? [Y/n] > ")
        if answer.lower().startswith("n"):
            yield "Alright, let's adjust.\n\n"
            prefs = await self._gather_preferences(context)
            context.store(JOBHUNT_PREF_KEY, prefs)
            blank()

        # ── Search ──
        yield "## 🔍 Searching for Jobs\n\n"
        yield f"   Platforms: {', '.join(p.value for p in context.config.search.platforms)}\n"
        yield f"   Keywords: {', '.join(context.config.search.search_terms)}\n\n"

        spinner = make_spinner("Searching all platforms...")
        with spinner:
            try:
                jobs = context.orchestrator.search_agent.search()
            except Exception as e:
                logger.error("Search failed: %s", e)
                yield f"❌ Search failed: {e}\n"
                return

        if not jobs:
            yield "No new jobs found. Try adjusting your search terms.\n"
            return

        yield f"✨ Found **{len(jobs)}** new jobs!\n\n"

        # ── Enrich ──
        yield "### Enriching job details...\n\n"
        prog = make_progress("Enriching jobs")
        with prog:
            task = prog.add_task("Fetching descriptions...", total=len(jobs))
            enriched = []
            for j in jobs:
                try:
                    enriched.append(context.orchestrator.search_agent.enrich_job(j))
                except Exception:
                    enriched.append(j)
                prog.update(task, advance=1)

        yield f"✅ Enriched {len(enriched)} jobs\n\n"

        # ── Rank ──
        yield "### 📊 Ranking jobs by match score...\n\n"
        prog2 = make_progress("Ranking jobs")
        ranked: list[tuple[dict[str, Any], dict[str, Any]]] = []
        with prog2:
            task2 = prog2.add_task("Scoring...", total=len(enriched))
            for j in enriched:
                try:
                    ranking = context.orchestrator.ranking_agent.rank(j, context.candidate_profile)
                    ranked.append((j, ranking))
                except Exception as e:
                    logger.warning("Rank failed: %s", e)
                prog2.update(task2, advance=1)

        ranked.sort(key=lambda x: x[1].get("score", 0), reverse=True)

        yield f"✅ Ranked {len(ranked)} jobs\n\n"

        # ── Show top results ──
        blank()
        console.print(jobs_table(
            [{"title": j.get("title"), "company": j.get("company"),
              "score": r.get("score"), "decision": {"decision": "PENDING"},
              "ranking": r}
             for j, r in ranked[:20]]
        ))
        blank()

        # ── Apply flow ──
        top_n_str = await context.ask(" How many top matches to review? [10] > ")
        top_n = 10
        if top_n_str.strip():
            try:
                top_n = max(1, min(int(top_n_str), len(ranked)))
            except ValueError:
                pass

        candidates = ranked[:top_n]

        for idx, (job, ranking) in enumerate(candidates, 1):
            blank()
            divider()
            blank()
            yield f"### Job #{idx}: {job.get('title')} at {job.get('company')}\n\n"

            score = ranking.get("score", 0)
            style = "score_high" if score >= 80 else "score_mid" if score >= 60 else "score_low"
            yield f"**Match Score:** [{style}]{score:.0f}/100[/]\n\n"

            yield f"**Company:** {job.get('company', '—')}\n"
            yield f"**Role:** {job.get('title', '—')}\n"
            yield f"**Location:** {job.get('location', '—')}\n"
            yield f"**Salary:** {job.get('salary', 'Not listed')}\n"
            yield f"**Platform:** {job.get('platform', '—')}\n\n"

            blank()
            console.print(score_breakdown_table(ranking))
            blank()

            # Decision
            if score >= context.config.ranking.min_score_threshold:
                try:
                    decision = context.orchestrator.application_agent.decide(job, ranking)
                except Exception as e:
                    logger.warning("Decision failed: %s", e)
                    decision = {"decision": "REVIEW", "confidence": 0.5,
                                "reasoning": "AI unavailable, manual review needed"}

                dec = decision.get("decision", "SKIP")
                reason = decision.get("reasoning", "")
                conf = decision.get("confidence", 0)

                yield f"**Decision:** {dec}  |  **Confidence:** {conf:.0%}\n\n"
                if reason:
                    yield f"> {reason}\n\n"

                if dec == "SKIP":
                    yield "⏭️  Skipping...\n"
                    continue

                if dec == "APPLY" and conf >= context.config.ranking.confidence_threshold:
                    blank()
                    act = await context.ask(f" Apply to {job.get('title')} at {job.get('company')}? [Y/n] > ")
                    if act.lower().startswith("n"):
                        yield "⏭️  Skipped by user.\n"
                        continue

                    yield "\n### 📄 Generating documents...\n\n"

                    try:
                        resume_path = context.orchestrator.resume_agent.select_best_resume(job)
                        summary = context.orchestrator.resume_agent.tailor_summary(job)
                        cover = context.orchestrator.cover_letter_agent.generate(job)
                        cl_path = context.orchestrator.cover_letter_agent.save(job, cover)

                        yield f"**Resume:** {resume_path}\n"
                        yield f"**Cover Letter:** {cl_path}\n\n"

                        # Record
                        context.orchestrator.tracking_agent.record_application(
                            job=job, ranking=ranking, decision=decision,
                            resume_path=resume_path, cover_letter_path=cl_path,
                        )
                        yield "✅ **Application recorded!**\n\n"
                    except Exception as e:
                        logger.error("Application failed: %s", e)
                        yield f"❌ Failed: {e}\n"
                else:
                    blank()
                    act = await context.ask(f" Review application for {job.get('title')} at {job.get('company')}? [Y/n] > ")
                    if not act.lower().startswith("n"):
                        yield "📝 Marked for review.\n"
                        context.orchestrator.tracking_agent.record_application(
                            job=job, ranking=ranking,
                            decision={"decision": "REVIEW", "confidence": conf, "reasoning": reason},
                        )
            else:
                yield f"⏭️  Score {score} below threshold — skipping.\n"

        blank()
        divider()
        blank()
        yield "## ✅ Job Hunt Complete!\n\n"
        summary = context.orchestrator.tracking_agent.generate_daily_report()
        yield f"**Total applications recorded:** {summary.get('total_applied', 0)}\n"
        yield f"**Total reviewed:** {summary.get('total_ranked', 0)}\n"
        yield f"**Average score:** {summary.get('avg_score', 0):.1f}\n\n"

        # Sync sheets
        try:
            context.orchestrator.tracking_agent.sync_to_sheets()
            yield "📊 Synced to Google Sheets.\n" if context.config.google_sheets.enabled else ""
        except Exception:
            pass

    async def _gather_preferences(self, context: PluginContext) -> dict[str, Any]:
        prefs: dict[str, Any] = {}

        blank()
        console.print("Let's set up your job hunt preferences.\n", style="text")

        role = await context.ask(" Preferred role (e.g. AI Engineer, Founding Engineer) > ")
        prefs["role"] = role.strip() or "AI Engineer"

        remote = await context.ask(" Remote only? [Y/n] > ")
        prefs["remote"] = "Remote" if not remote.lower().startswith("n") else "On-site/Hybrid"

        salary = await context.ask(" Minimum salary expectation (e.g. 100k or 'Any') > ")
        prefs["salary"] = salary.strip() or "Any"

        exp_str = await context.ask(" Years of experience > ")
        try:
            prefs["experience"] = int(exp_str.strip())
        except (ValueError, AttributeError):
            prefs["experience"] = 0

        location = await context.ask(" Preferred location (or 'Remote') > ")
        prefs["location"] = location.strip() or "Remote"

        blank()
        console.print(f"✅ Got it! Searching for **{prefs['role']}** roles.\n")
        blank()
        return prefs
