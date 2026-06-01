from __future__ import annotations

from typing import AsyncGenerator
from rich.console import Console

from plugins.base import Plugin, PluginContext


class ClearPlugin(Plugin):
    name = "clear"
    description = "Clear the terminal screen"
    aliases = ["cls"]

    async def execute(self, args: str, context: PluginContext) -> AsyncGenerator[str, None]:
        Console().clear()
        yield ""
