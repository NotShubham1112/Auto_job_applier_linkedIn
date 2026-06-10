"""ThinkingBox widget — animated multi-step "thinking" indicator.

Shows a list of sub-tasks the agent is performing, each with a status
icon (○, ●, ✓, ✗). Minimal design: no borders, just text hierarchy.

Example:
    Thinking
      ● Reading files
      ✓ Searching docs
      ○ Creating plan
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from rich.text import Text
from textual.containers import Vertical
from textual.reactive import reactive
from textual.widgets import Static

from cli.styles.palette import PALETTE


# ── Step model ─────────────────────────────────────────────────────────────


STEP_PENDING = "pending"
STEP_RUNNING = "running"
STEP_DONE = "done"
STEP_ERROR = "error"


STEP_ICONS: dict[str, str] = {
    STEP_PENDING: "\u25cb",   # ○
    STEP_RUNNING: "\u25cf",   # ●
    STEP_DONE: "\u2713",      # ✓
    STEP_ERROR: "\u2717",     # ✗
}


@dataclass
class ThinkingStep:
    """A single line inside the ThinkingBox."""

    label: str
    status: str = STEP_PENDING
    detail: str = ""


class ThinkingBox(Vertical):
    """Container that renders a list of ThinkingSteps with icons.

    The widget exposes a small imperative API:
      - ``set_steps(labels)`` to define the plan
      - ``start(i)`` / ``complete(i)`` / ``fail(i)`` to update state
    """

    DEFAULT_CSS = """
    ThinkingBox {
        background: #000000;
        height: auto;
        margin: 0 0;
        padding: 0 0;
    }

    ThinkingBox #thinking-title {
        color: #666666;
        height: 1;
        padding: 0 0;
    }

    ThinkingBox .thinking-step {
        height: 1;
        color: #666666;
        padding: 0 0;
    }

    ThinkingBox .thinking-step.running {
        color: #ffffff;
        text-style: bold;
    }

    ThinkingBox .thinking-step.done {
        color: #3b82f6;
    }

    ThinkingBox .thinking-step.error {
        color: #f43f5e;
    }

    ThinkingBox .thinking-step.pending {
        color: #666666;
    }

    ThinkingBox .step-icon {
        width: 3;
    }
    """

    steps: reactive[list[ThinkingStep]] = reactive(
        list, recompose=False, always_update=False
    )
    title_text: reactive[str] = reactive("Thinking")

    def __init__(
        self,
        steps: Iterable[str] | None = None,
        title: str = "Thinking",
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self._title_widget: Static | None = None
        self._step_widgets: list[Static] = []
        self.steps = [ThinkingStep(label=s) for s in (steps or [])]
        self.title_text = title

    def compose(self):
        title = Static(self._render_title(), id="thinking-title")
        self._title_widget = title
        yield title
        for i, step in enumerate(self.steps):
            w = Static(self._render_step(i), classes=f"thinking-step {step.status}")
            self._step_widgets.append(w)
            yield w

    def watch_title_text(self, _old: str, _new: str) -> None:
        if hasattr(self, "_title_widget") and self._title_widget is not None:
            self._title_widget.update(self._render_title())

    def watch_steps(self, _old: list[ThinkingStep], _new: list[ThinkingStep]) -> None:
        if not hasattr(self, "_step_widgets") or not self._step_widgets:
            return
        for i, widget in enumerate(self._step_widgets):
            if i < len(_new):
                widget.set_class(_new[i].status == STEP_RUNNING, "running")
                widget.set_class(_new[i].status == STEP_DONE, "done")
                widget.set_class(_new[i].status == STEP_ERROR, "error")
                widget.set_class(_new[i].status == STEP_PENDING, "pending")
                widget.update(self._render_step(i))
            else:
                widget.display = False

    # ── Public API ──────────────────────────────────────────────────────

    def set_steps(self, labels: Iterable[str]) -> None:
        self.steps = [ThinkingStep(label=s) for s in labels]
        self._rebuild_step_widgets()
        self.refresh()

    def add_step(self, label: str) -> int:
        self.steps.append(ThinkingStep(label=label))
        self._append_step_widget(len(self.steps) - 1)
        return len(self.steps) - 1

    def start(self, index: int) -> None:
        if 0 <= index < len(self.steps):
            self.steps[index].status = STEP_RUNNING
            self._update_step_widget(index)

    def complete(self, index: int) -> None:
        if 0 <= index < len(self.steps):
            self.steps[index].status = STEP_DONE
            self._update_step_widget(index)

    def fail(self, index: int, detail: str = "") -> None:
        if 0 <= index < len(self.steps):
            self.steps[index].status = STEP_ERROR
            if detail:
                self.steps[index].detail = detail
            self._update_step_widget(index)

    def reset(self) -> None:
        self.steps = []
        self._step_widgets = []
        self.refresh()

    def show(self) -> None:
        self.display = True
        self.styles.height = "auto"

    def hide(self) -> None:
        self.display = False

    # ── Internal helpers ────────────────────────────────────────────────

    def _rebuild_step_widgets(self) -> None:
        for w in self._step_widgets:
            w.remove()
        self._step_widgets = []
        for i in range(len(self.steps)):
            self._append_step_widget(i)
        self.refresh(layout=True)

    def _append_step_widget(self, index: int) -> None:
        w = Static(
            self._render_step(index),
            classes=f"thinking-step {self.steps[index].status}",
        )
        self._step_widgets.append(w)
        self.mount(w)

    def _update_step_widget(self, index: int) -> None:
        if index < 0 or index >= len(self._step_widgets):
            return
        widget = self._step_widgets[index]
        step = self.steps[index]
        for cls in ("running", "done", "error", "pending"):
            widget.set_class(step.status == cls, cls)
        widget.update(self._render_step(index))

    def _render_title(self) -> Text:
        return Text(f" {self.title_text}", style=f"{PALETTE.text_muted}")

    def _render_step(self, index: int) -> Text:
        step = self.steps[index]
        icon = STEP_ICONS.get(step.status, " ")
        text = Text()
        text.append(f"  {icon} ", style=self._icon_style(step.status))
        text.append(step.label, style=self._label_style(step.status))
        if step.detail:
            text.append(f"  {step.detail}", style=PALETTE.text_muted)
        return text

    def _icon_style(self, status: str) -> str:
        return {
            STEP_PENDING: PALETTE.text_muted,
            STEP_RUNNING: PALETTE.accent,
            STEP_DONE: PALETTE.primary,
            STEP_ERROR: PALETTE.error,
        }.get(status, PALETTE.text_muted)

    def _label_style(self, status: str) -> str:
        if status == STEP_RUNNING:
            return f"bold {PALETTE.text}"
        if status == STEP_DONE:
            return PALETTE.primary
        if status == STEP_ERROR:
            return PALETTE.error
        return PALETTE.text_muted
