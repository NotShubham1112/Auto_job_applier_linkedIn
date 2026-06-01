from __future__ import annotations

import logging
from typing import Any, AsyncGenerator, Optional

from rich.console import Console

from agents.workflow import JobApplicationOrchestrator
from chat.memory import ConversationMemory
from config.settings import AppConfig
from database.repository import Repository
from plugins.base import Plugin, PluginContext, PluginRegistry
from services.groq_service import GroqService
from ui.components import agent_panel, blank, console, divider, stream_text
from ui.styles import Palette

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an AI Job Hunting Assistant running in a terminal.

The user can type:
- Slash commands like /jobhunt, /search, /status, /help, etc.
- Natural language questions about careers, resumes, interviews, etc.

For natural language input, respond helpfully and concisely.
Use markdown for formatting. Be warm but professional.

If the user asks about features or what you can do, tell them to type /help.

Candidate profile: {profile}
"""


class CommandRouter:
    """Routes user input to the appropriate handler.

    Priority:
    1. Slash commands → plugin system
    2. Natural language → LLM chat completion
    """

    def __init__(
        self,
        config: AppConfig,
        repo: Repository,
        groq: GroqService,
        orchestrator: JobApplicationOrchestrator,
        candidate_profile: str,
        memory: ConversationMemory,
        console: Console,
    ) -> None:
        self.config = config
        self.repo = repo
        self.groq = groq
        self.orchestrator = orchestrator
        self.candidate_profile = candidate_profile
        self.memory = memory
        self.console = console
        self.registry = PluginRegistry()

    def register(self, plugin: Plugin) -> None:
        """Register a plugin with the router."""
        self.registry.register(plugin)

    async def route(self, user_input: str) -> AsyncGenerator[str, None]:
        """Route user input to the right handler.

        Yields response tokens for streaming display.
        """
        user_input = user_input.strip()
        if not user_input:
            return

        # Store user message in memory
        self.memory.add_message("user", user_input)

        plugin, args = self.registry.resolve(user_input)

        if plugin is not None:
            # ── Slash command ──
            context = PluginContext(
                config=self.config,
                repo=self.repo,
                groq=self.groq,
                orchestrator=self.orchestrator,
                candidate_profile=self.candidate_profile,
                session_id=self.memory.session_id,
                console=self.console,
                memory={"_registry": self.registry},
            )
            try:
                async for token in plugin.execute(args, context):
                    yield token
            except SystemExit:
                raise
            except Exception as e:
                logger.exception("Plugin %s failed", plugin.name)
                yield f"\n\n❌ **Error:** {e}\n"
        else:
            # ── Natural language → LLM ──
            async for token in self._llm_chat(user_input):
                yield token

    async def _llm_chat(self, user_input: str) -> AsyncGenerator[str, None]:
        """Stream a response from the LLM for natural language input."""
        profile = self.candidate_profile

        # Build context from recent history
        recent = self.memory.get_recent_context(10)
        system_msg = {
            "role": "system",
            "content": SYSTEM_PROMPT.format(profile=profile[:1500] if profile else "No profile."),
        }
        messages = [system_msg] + recent

        messages.append({"role": "user", "content": user_input})

        try:
            client = self.groq._get_client()
            response = client.chat.completions.create(
                model=self.config.ai.groq_model.value,
                messages=messages,
                temperature=self.config.ai.temperature,
                max_tokens=self.config.ai.max_tokens,
                stream=True,
            )
            for chunk in response:
                if chunk.choices and len(chunk.choices) > 0:
                    delta = chunk.choices[0].delta
                    if delta and delta.content:
                        yield delta.content
        except Exception as e:
            logger.error("LLM chat failed, falling back: %s", e)
            try:
                text = self.groq.completion(messages)
                yield text
            except Exception as e2:
                yield f"\n\n❌ I'm having trouble connecting to the AI. Error: {e2}\n"
                yield "Please check your API key and try again.\n"
