"""AgentBoard widget — visualize multiple agents running in parallel.

Displays a list of agents with their current status (RUNNING, WAITING,
DONE, ERROR). Updates live as the orchestrator moves agents through
their lifecycle.

Example:
    ╭─────────────────────────────────╮
    │ Active Agents                   │
    ├─────────────────────────────────┤
    │ 🔍 Research Agent      RUNNING  │
    │ ⚙️ Backend Agent       RUNNING  │
    │ 🎨 Frontend Agent      WAITING  │
    │ 🧪 Testing Agent       WAITING  │
    ╰─────────────────────────────────╯
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from rich.text import Text
from textual.containers import Vertical
from textual.reactive import reactive
from textual.widgets import Static

from cli.styles.palette import PALETTE


# ── Agent model ────────────────────────────────────────────────────────────

AGENT_PENDING = "pending"
AGENT_RUNNING = "running"
AGENT_WAITING = "waiting"
AGENT_DONE = "done"
AGENT_ERROR = "error"

AGENT_STATUS_LABELS: dict[str, str] = {
    AGENT_PENDING: "PENDING",
    AGENT_RUNNING: "RUNNING",
    AGENT_WAITING: "WAITING",
    AGENT_DONE: "DONE",
    AGENT_ERROR: "ERROR",
}

AGENT_STATUS_STYLES: dict[str, str] = {
    AGENT_PENDING: "#ffffff",
    AGENT_RUNNING: "#3b82f6",
    AGENT_WAITING: "#ffffff",
    AGENT_DONE: "#ffffff",
    AGENT_ERROR: "#f43f5e",
}

# Default agent icons by name (the spec uses 🔍 ⚙️ 🎨 🧪)
DEFAULT_AGENT_ICONS: dict[str, str] = {
    "research": "\U0001f50d",   # 🔍
    "backend": "\u2699\ufe0f",  # ⚙️
    "frontend": "\U0001f3a8",   # 🎨
    "testing": "\U0001f9ea",    # 🧪
    "general": "\U0001f916",    # 🤖
    "ranking": "\U0001f4ca",    # 📊
    "search": "\U0001f50d",     # 🔍
    "apply": "\U0001f4e4",      # 📤
    "resume": "\U0001f4c4",     # 📄
    "cover": "\u270d\ufe0f",    # ✍️
    "tracking": "\U0001f4cb",   # 📋
}


@dataclass
class AgentEntry:
    """A single agent in the board."""

    name: str
    status: str = AGENT_PENDING
    icon: str = ""
    detail: str = ""


# ── Widget ────────────────────────────────────────────────────────────────


class AgentRow(Static):
    """A single row in the agent board."""

    DEFAULT_CSS = """
    AgentRow {
        height: 1;
        color: #ffffff;
        padding: 0 1;
    }

    AgentRow.running {
        color: #3b82f6;
    }

    AgentRow.waiting {
        color: #ffffff;
    }

    AgentRow.done {
        color: #ffffff;
    }

    AgentRow.error {
        color: #f43f5e;
    }

    AgentRow.pending {
        color: #ffffff;
    }
    """

    def __init__(self, agent: AgentEntry, **kwargs) -> None:
        super().__init__(**kwargs)
        self.agent = agent
        self.add_class(agent.status)
        self._render()

    def update_agent(self, agent: AgentEntry) -> None:
        # Toggle classes based on the new status
        for s in (
            AGENT_PENDING, AGENT_RUNNING, AGENT_WAITING,
            AGENT_DONE, AGENT_ERROR,
        ):
            self.set_class(agent.status == s, s)
        self.agent = agent
        self._render()

    def _render(self) -> None:
        text = Text()
        icon = self.agent.icon or DEFAULT_AGENT_ICONS.get(
            self.agent.name.lower(), "\U0001f916"
        )
        text.append(f" {icon} ", style="")
        text.append(f"{self.agent.name:<22}", style="")
        if self.agent.detail:
            text.append(f"{self.agent.detail:<14}", style="#ffffff")
        else:
            text.append(" " * 14, style="")
        text.append(
            AGENT_STATUS_LABELS.get(self.agent.status, "?"),
            style=AGENT_STATUS_STYLES.get(self.agent.status, "#ffffff"),
        )
        self.update(text)


class AgentBoard(Vertical):
    """The right-side panel that shows all running agents.

    The board keeps an internal list of agents and re-renders the
    rows when their status changes. If you set ``agents`` to a new
    list, the board recomposes the rows.
    """

    DEFAULT_CSS = """
    AgentBoard {
        background: #000000;
        height: 1fr;
        padding: 1 1;
    }

    AgentBoard #agent-board-title {
        color: #ffffff;
        text-style: bold;
        height: 1;
        padding: 0 1;
        border-bottom: solid #3b82f6;
        margin-bottom: 1;
    }
    """

    agents: reactive[list[AgentEntry]] = reactive(list, recompose=False)
    title: reactive[str] = reactive("Active Agents")

    def __init__(
        self,
        agents: Optional[list[AgentEntry]] = None,
        title: str = "Active Agents",
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        # Initialize internal state BEFORE setting reactives so that
        # watchers don't crash if they fire on init.
        self._title_widget: Optional[Static] = None
        self._row_widgets: list[AgentRow] = []
        self.agents = list(agents or [])
        self._title = title

    def compose(self):
        self._title_widget = Static(
            f" {self.title} ", id="agent-board-title"
        )
        yield self._title_widget
        for agent in self.agents:
            row = AgentRow(agent)
            self._row_widgets.append(row)
            yield row

    def on_mount(self) -> None:
        # If no agents were passed at construction, add a few defaults
        if not self.agents:
            self.set_agents([
                AgentEntry(name="Research Agent", status=AGENT_WAITING),
                AgentEntry(name="Ranking Agent", status=AGENT_WAITING),
                AgentEntry(name="Resume Agent", status=AGENT_WAITING),
                AgentEntry(name="Apply Agent", status=AGENT_WAITING),
            ])

    def watch_agents(self, _old: list[AgentEntry], new: list[AgentEntry]) -> None:
        """Re-render rows when the agents list changes."""
        if not hasattr(self, "_row_widgets"):
            return
        # Remove all existing rows from the DOM
        for row in self._row_widgets:
            row.remove()
        self._row_widgets = []
        # Add fresh rows
        for agent in new:
            row = AgentRow(agent)
            self._row_widgets.append(row)
            self.mount(row)
        self.refresh(layout=True)

    # ── Public API ──────────────────────────────────────────────────────

    def set_agents(self, agents: list[AgentEntry]) -> None:
        """Replace the entire list of agents."""
        self.agents = list(agents)

    def add_agent(self, agent: AgentEntry) -> None:
        """Append a new agent."""
        self.agents = self.agents + [agent]

    def set_status(
        self,
        name: str,
        status: str,
        detail: str = "",
    ) -> None:
        """Update the status of a single agent by name.

        If no agent with that name exists, it is created and added.
        """
        updated: list[AgentEntry] = []
        found = False
        for a in self.agents:
            if a.name == name:
                a.status = status
                if detail:
                    a.detail = detail
                found = True
            updated.append(a)
        if not found:
            updated.append(AgentEntry(name=name, status=status, detail=detail))
        self.agents = updated

    def set_all(self, status: str) -> None:
        """Set every agent to the same status (e.g. WAITING)."""
        for a in self.agents:
            a.status = status
        self.agents = list(self.agents)

    def clear(self) -> None:
        self.set_agents([])
