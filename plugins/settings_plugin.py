from __future__ import annotations

from typing import AsyncGenerator

from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from plugins.base import Plugin, PluginContext
from ui.components import blank, console
from ui.styles import Palette

SETTINGS_MAP = {
    "search terms": ("search_terms", "search"),
    "location": ("search_location", "search"),
    "remote only": ("remote_only", "search"),
    "platforms": ("platforms", "search"),
    "min score": ("min_score_threshold", "ranking"),
    "confidence": ("confidence_threshold", "ranking"),
    "groq model": ("groq_model", "ai"),
    "temperature": ("temperature", "ai"),
    "default resume": ("default_resume_path", "resume"),
    "experience": ("years_of_experience", "resume"),
}


class SettingsPlugin(Plugin):
    name = "settings"
    description = "View and modify configuration settings"
    aliases = ["config", "prefs", "preferences"]

    async def execute(self, args: str, context: PluginContext) -> AsyncGenerator[str, None]:
        if not args:
            yield self._show_settings(context)
            return

        parts = args.split(maxsplit=2)
        subcmd = parts[0].lower()

        if subcmd in ("show", "view", "list"):
            yield self._show_settings(context)
        elif subcmd == "set" and len(parts) >= 3:
            yield await self._set_setting(parts[1], parts[2], context)
        elif subcmd == "get" and len(parts) >= 2:
            yield self._get_setting(parts[1], context)
        else:
            yield self._help()

    def _show_settings(self, context: PluginContext) -> str:
        c = context.config
        lines = ["## ⚙️ Current Settings\n\n"]
        lines.append("### 🔍 Search\n")
        lines.append(f"  • Search terms: `{', '.join(c.search.search_terms)}`\n")
        lines.append(f"  • Remote only: `{c.search.remote_only}`\n")
        lines.append(f"  • Location: `{c.search.search_location or 'Any'}`\n")
        lines.append(f"  • Platforms: `{', '.join(p.value for p in c.search.platforms)}`\n")
        lines.append(f"  • Easy Apply only: `{c.search.easy_apply_only}`\n\n")

        lines.append("### 🤖 AI\n")
        lines.append(f"  • Provider: `{c.ai.provider.value}`\n")
        lines.append(f"  • Model: `{c.ai.groq_model.value}`\n")
        lines.append(f"  • Temperature: `{c.ai.temperature}`\n\n")

        lines.append("### 📄 Resume\n")
        lines.append(f"  • Default resume: `{c.resume.default_resume_path}`\n")
        lines.append(f"  • Years experience: `{c.resume.years_of_experience}`\n\n")

        lines.append("### 📊 Ranking\n")
        lines.append(f"  • Min score: `{c.ranking.min_score_threshold}`\n")
        lines.append(f"  • Confidence: `{c.ranking.confidence_threshold}`\n\n")

        lines.append("Use `/settings set <key> <value>` to change a setting.\n")
        lines.append("Example: `/settings set min score 70`\n")
        return "".join(lines)

    def _get_setting(self, key: str, context: PluginContext) -> str:
        key_lower = key.lower().strip()
        for setting_name, (attr, section) in SETTINGS_MAP.items():
            if setting_name.startswith(key_lower) or key_lower.startswith(setting_name):
                section_obj = getattr(context.config, section, None)
                if section_obj:
                    val = getattr(section_obj, attr, "N/A")
                    return f"**{setting_name}** = `{val}`\n"
        return f"Unknown setting: `{key}`\n"

    async def _set_setting(self, key: str, value: str, context: PluginContext) -> str:
        key_lower = key.lower().strip()
        for setting_name, (attr, section) in SETTINGS_MAP.items():
            if setting_name.startswith(key_lower) or key_lower.startswith(setting_name):
                section_obj = getattr(context.config, section, None)
                if not section_obj:
                    return f"❌ Cannot find section `{section}`\n"
                old_val = getattr(section_obj, attr, None)
                try:
                    if isinstance(old_val, bool):
                        setattr(section_obj, attr, value.lower() in ("true", "yes", "1"))
                    elif isinstance(old_val, int):
                        setattr(section_obj, attr, int(value))
                    elif isinstance(old_val, float):
                        setattr(section_obj, attr, float(value))
                    elif isinstance(old_val, list):
                        setattr(section_obj, attr, [v.strip() for v in value.split(",")])
                    else:
                        setattr(section_obj, attr, value)
                except (ValueError, TypeError) as e:
                    return f"❌ Invalid value: {e}\n"
                return f"✅ **{setting_name}** changed from `{old_val}` to `{getattr(section_obj, attr)}`\n"
        return f"❌ Unknown setting: `{key}`\n"

    def _help(self) -> str:
        return (
            "Usage:\n"
            "  `/settings` — show all settings\n"
            "  `/settings get <key>` — get a specific setting\n"
            "  `/settings set <key> <value>` — change a setting\n"
        )
