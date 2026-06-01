from __future__ import annotations

import logging
from typing import AsyncGenerator

from rich.markdown import Markdown
from rich.panel import Panel

from plugins.base import Plugin, PluginContext
from ui.components import blank, console, stream_text
from ui.styles import Palette

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an AI Job Hunting Assistant — a friendly, expert career coach embedded in a terminal application.

You help users with:
- Job search strategy and positioning
- Resume and cover letter optimization
- Interview preparation and practice
- Career advice and salary negotiation
- AI engineering industry insights
- Startup career guidance
- LinkedIn profile optimization
- Technical skill development for AI roles

Rules:
- Be concise but warm. Use markdown for formatting.
- Base answers on the candidate profile when relevant.
- When asked about specific jobs or applications, direct the user to use /jobs or /status.
- Never invent experience or qualifications for the user.
- Keep responses under 3 paragraphs unless the user asks for detail.
- Use a conversational, mentoring tone.

Candidate Profile Summary:
{profile_summary}
"""


class ChatPlugin(Plugin):
    """General AI assistant mode — answers career questions, gives advice.

    Mode 2 of the system.
    """

    name = "chat"
    description = "General AI assistant mode — career advice, interview prep, questions"
    aliases = ["ask", "advice"]

    async def execute(self, args: str, context: PluginContext) -> AsyncGenerator[str, None]:
        if not args:
            yield "Hi! I'm your AI career assistant. Ask me anything about:\n\n"
            yield "• Resume optimization\n"
            yield "• Interview preparation\n"
            yield "• Career strategy\n"
            yield "• AI engineering roles\n"
            yield "• Salary negotiation\n"
            yield "• Startup advice\n\n"
            yield "What would you like to discuss?\n"
            return

        async for token in self._stream_llm_response(args, context):
            yield token

    async def _stream_llm_response(
        self, question: str, context: PluginContext
    ) -> AsyncGenerator[str, None]:
        profile = context.candidate_profile
        profile_summary = profile[:1500] if profile else "No profile loaded."

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT.format(profile_summary=profile_summary)},
            {"role": "user", "content": question},
        ]

        try:
            full = ""
            async for chunk in self._stream_groq(messages, context):
                full += chunk
                yield chunk
        except Exception as e:
            logger.error("Chat LLM error: %s", e)
            yield f"\n\n> ❌ Sorry, I encountered an error: {e}\n"

    async def _stream_groq(
        self, messages: list[dict], context: PluginContext
    ) -> AsyncGenerator[str, None]:
        """Stream tokens from Groq."""
        try:
            client = context.groq._get_client()
            response = client.chat.completions.create(
                model=context.config.ai.groq_model.value,
                messages=messages,
                temperature=context.config.ai.temperature,
                max_tokens=context.config.ai.max_tokens,
                stream=True,
            )
            for chunk in response:
                if chunk.choices and len(chunk.choices) > 0:
                    delta = chunk.choices[0].delta
                    if delta and delta.content:
                        yield delta.content
        except Exception as e:
            logger.error("Groq streaming failed: %s", e)
            # Fallback to non-streaming
            text = context.groq.completion(messages)
            yield text
