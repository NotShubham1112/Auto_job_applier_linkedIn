"""Developer-focused plugins for the OpenCode-style commands.

These implement /research, /build, /fix, /review, /architect, /debug,
/ship. They follow the same plugin protocol as the existing job-hunt
plugins so they slot in transparently.
"""

from __future__ import annotations

import logging
from typing import AsyncGenerator

from plugins.base import Plugin, PluginContext

logger = logging.getLogger(__name__)


def _prompt_for_args(args: str, prompt: str, context: PluginContext) -> str:
    """Async helper that prompts the user for missing args (no-op for now)."""
    return args


class ResearchPlugin(Plugin):
    """Deep research on a topic using the LLM."""

    name = "research"
    description = "Research a topic (LLM deep-dive)"
    aliases = ["rs"]

    async def execute(self, args: str, context: PluginContext) -> AsyncGenerator[str, None]:
        if not args:
            yield "**Research mode**\n\n"
            yield "Tell me what to research. Examples:\n"
            yield "- `market sizing for agentic dev tools`\n"
            yield "- `best practices for RAG retrieval in 2026`\n"
            yield "- `state of open-source LLM serving`\n"
            return

        messages = [
            {"role": "system", "content": (
                "You are a senior research analyst. Investigate the topic "
                "thoroughly, cite known sources where possible, and structure "
                "the answer with sections: Overview, Key Findings, Trade-offs, "
                "Open Questions, Sources."
            )},
            {"role": "user", "content": args},
        ]
        async for chunk in self._stream(messages, context):
            yield chunk

    async def _stream(self, messages, context):
        try:
            client = context.groq._get_client()
            response = client.chat.completions.create(
                model=context.config.ai.groq_model.value,
                messages=messages,
                temperature=0.3,
                max_tokens=context.config.ai.max_tokens,
                stream=True,
            )
            for chunk in response:
                if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            yield f"\n\n_Research failed: {e}_\n"


class BuildPlugin(Plugin):
    """Build a plan / scaffold a project."""

    name = "build"
    description = "Build a plan / scaffold a project"
    aliases = ["b"]

    async def execute(self, args: str, context: PluginContext) -> AsyncGenerator[str, None]:
        if not args:
            yield "**Build mode**\n\n"
            yield "Describe what to build. Examples:\n"
            yield "- `REST API for a todo app in FastAPI`\n"
            yield "- `CI/CD pipeline for a Python service`\n"
            yield "- `Authentication module with JWT and refresh tokens`\n"
            return

        messages = [
            {"role": "system", "content": (
                "You are a senior engineer. Produce a concrete, step-by-step "
                "build plan: goals, file structure, dependencies, "
                "implementation order, and verification."
            )},
            {"role": "user", "content": args},
        ]
        async for chunk in self._stream(messages, context):
            yield chunk

    async def _stream(self, messages, context):
        try:
            client = context.groq._get_client()
            response = client.chat.completions.create(
                model=context.config.ai.groq_model.value,
                messages=messages,
                temperature=0.3,
                max_tokens=context.config.ai.max_tokens,
                stream=True,
            )
            for chunk in response:
                if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            yield f"\n\n_Build planning failed: {e}_\n"


class FixPlugin(Plugin):
    """Diagnose and fix a problem."""

    name = "fix"
    description = "Diagnose and fix a problem"
    aliases = []

    async def execute(self, args: str, context: PluginContext) -> AsyncGenerator[str, None]:
        if not args:
            yield "**Fix mode**\n\n"
            yield "Describe the problem. Include error messages, stack traces, "
            yield "and what you tried. Example: `pip install fails with "
            yield "ModuleNotFoundError after upgrading to Python 3.13`\n"
            return

        messages = [
            {"role": "system", "content": (
                "You are a senior debugger. Diagnose the issue, list likely "
                "root causes in order of probability, and propose the minimum "
                "viable fix. Be specific and concrete."
            )},
            {"role": "user", "content": args},
        ]
        async for chunk in self._stream(messages, context):
            yield chunk

    async def _stream(self, messages, context):
        try:
            client = context.groq._get_client()
            response = client.chat.completions.create(
                model=context.config.ai.groq_model.value,
                messages=messages,
                temperature=0.2,
                max_tokens=context.config.ai.max_tokens,
                stream=True,
            )
            for chunk in response:
                if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            yield f"\n\n_Fix analysis failed: {e}_\n"


class ReviewPlugin(Plugin):
    """Review code or decisions."""

    name = "review"
    description = "Review code or decisions"
    aliases = ["rv"]

    async def execute(self, args: str, context: PluginContext) -> AsyncGenerator[str, None]:
        if not args:
            yield "**Review mode**\n\n"
            yield "Paste the code, design, or decision you want reviewed.\n"
            return

        messages = [
            {"role": "system", "content": (
                "You are a meticulous reviewer. Identify issues, suggest "
                "improvements, call out edge cases, and praise what works. "
                "Be direct and structured."
            )},
            {"role": "user", "content": args},
        ]
        async for chunk in self._stream(messages, context):
            yield chunk

    async def _stream(self, messages, context):
        try:
            client = context.groq._get_client()
            response = client.chat.completions.create(
                model=context.config.ai.groq_model.value,
                messages=messages,
                temperature=0.2,
                max_tokens=context.config.ai.max_tokens,
                stream=True,
            )
            for chunk in response:
                if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            yield f"\n\n_Review failed: {e}_\n"


class ArchitectPlugin(Plugin):
    """Design a system architecture."""

    name = "architect"
    description = "Design a system architecture"
    aliases = ["arch"]

    async def execute(self, args: str, context: PluginContext) -> AsyncGenerator[str, None]:
        if not args:
            yield "**Architect mode**\n\n"
            yield "Describe the system. Examples:\n"
            yield "- `event-sourced order processing platform`\n"
            yield "- `multi-tenant SaaS with row-level security`\n"
            return

        messages = [
            {"role": "system", "content": (
                "You are a principal architect. Produce a system design: "
                "components, data flow, key trade-offs, scaling bottlenecks, "
                "and a recommended stack. Use diagrams-in-ASCII where useful."
            )},
            {"role": "user", "content": args},
        ]
        async for chunk in self._stream(messages, context):
            yield chunk

    async def _stream(self, messages, context):
        try:
            client = context.groq._get_client()
            response = client.chat.completions.create(
                model=context.config.ai.groq_model.value,
                messages=messages,
                temperature=0.3,
                max_tokens=context.config.ai.max_tokens,
                stream=True,
            )
            for chunk in response:
                if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            yield f"\n\n_Architect failed: {e}_\n"


class DebugPlugin(Plugin):
    """Debug a runtime issue."""

    name = "debug"
    description = "Debug a runtime issue"
    aliases = ["dbg"]

    async def execute(self, args: str, context: PluginContext) -> AsyncGenerator[str, None]:
        if not args:
            yield "**Debug mode**\n\n"
            yield "Paste the error, logs, or describe the bug.\n"
            return

        messages = [
            {"role": "system", "content": (
                "You are an expert debugger. Walk through possible causes, "
                "ranking by likelihood. For each cause, give: how to confirm, "
                "the fix, and how to prevent it from recurring."
            )},
            {"role": "user", "content": args},
        ]
        async for chunk in self._stream(messages, context):
            yield chunk

    async def _stream(self, messages, context):
        try:
            client = context.groq._get_client()
            response = client.chat.completions.create(
                model=context.config.ai.groq_model.value,
                messages=messages,
                temperature=0.2,
                max_tokens=context.config.ai.max_tokens,
                stream=True,
            )
            for chunk in response:
                if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            yield f"\n\n_Debug failed: {e}_\n"


class ShipPlugin(Plugin):
    """Ship a feature / finalize deliverables."""

    name = "ship"
    description = "Ship a feature / finalize deliverables"
    aliases = []

    async def execute(self, args: str, context: PluginContext) -> AsyncGenerator[str, None]:
        if not args:
            yield "**Ship mode**\n\n"
            yield "Describe what you're shipping. Example: `v1.0 of the "
            yield "LinkedIn applier with the new cover-letter agent`.\n"
            return

        messages = [
            {"role": "system", "content": (
                "You are a release manager. Produce a ship checklist: pre-flight "
                "tests, release notes, rollback plan, monitoring, and a "
                "post-launch review template."
            )},
            {"role": "user", "content": args},
        ]
        async for chunk in self._stream(messages, context):
            yield chunk

    async def _stream(self, messages, context):
        try:
            client = context.groq._get_client()
            response = client.chat.completions.create(
                model=context.config.ai.groq_model.value,
                messages=messages,
                temperature=0.2,
                max_tokens=context.config.ai.max_tokens,
                stream=True,
            )
            for chunk in response:
                if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            yield f"\n\n_Ship failed: {e}_\n"
