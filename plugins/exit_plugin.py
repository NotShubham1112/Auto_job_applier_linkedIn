from __future__ import annotations

from typing import AsyncGenerator

from plugins.base import Plugin, PluginContext


class ExitPlugin(Plugin):
    name = "exit"
    description = "Exit the application"
    aliases = ["quit", "bye", "q"]

    async def execute(self, args: str, context: PluginContext) -> AsyncGenerator[str, None]:
        yield "Goodbye! 👋\n"
        raise SystemExit(0)
