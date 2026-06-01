from __future__ import annotations

from typing import AsyncGenerator

from rich.table import Table
from rich.text import Text

from plugins.base import Plugin, PluginContext
from ui.components import console
from ui.styles import Palette


class HelpPlugin(Plugin):
    name = "help"
    description = "Show available commands and usage information"
    aliases = ["h", "commands"]

    async def execute(self, args: str, context: PluginContext) -> AsyncGenerator[str, None]:
        registry = context.memory.get("_registry")
        if registry is None:
            yield "# Available Commands\n\n"
            return

        commands = registry.commands_list()
        table = Table(
            title=Text(" Slash Commands ", style="bold primary"),
            box=None,
            border_style="secondary",
            padding=(0, 2),
            show_edge=False,
        )
        table.add_column("Command", style="bold secondary", no_wrap=True)
        table.add_column("Aliases", style="dim", no_wrap=True)
        table.add_column("Description", style="text")

        for cmd, aliases, desc in sorted(commands):
            table.add_row(cmd, aliases, desc)

        console.print(table)
        console.print()
        yield "Type `/command --help` for detailed usage on any command.\n"
        yield "Or just type naturally — I'll understand what you need.\n"
