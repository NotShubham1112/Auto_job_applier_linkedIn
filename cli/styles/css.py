"""BROWORK Textual CSS — OpenCode / Warp inspired look.

The visual grammar:
  - Near-black background, warm-orange accent (OpenCode feel)
  - Rounded borders, generous padding, lots of whitespace
  - Status bar pinned to the bottom, command palette in the middle
  - Streaming output auto-grows inside a scrollable log
"""

from __future__ import annotations


def get_css() -> str:
    """Return the full Textual CSS used by the BROWORK app."""
    return """
/* ── Screen-level ─────────────────────────────────────────────────────── */

Screen {
    background: #0a0a0a;
    color: #e6e6e6;
    layers: base overlay modal;
}

#app-grid {
    layout: vertical;
    height: 100%;
}

/* ── Boot / Loading screen ───────────────────────────────────────────── */

#boot-screen {
    align: center middle;
    background: #0a0a0a;
}

#boot-logo {
    width: auto;
    height: auto;
    color: #f4b183;
    text-style: bold;
}

#boot-tagline {
    color: #9a9a9a;
    text-align: center;
    padding: 1 0;
}

#boot-list {
    width: 50;
    height: auto;
    padding: 1 2;
}

#boot-list > .boot-line {
    height: 1;
    color: #9a9a9a;
}

#boot-list > .boot-line.done {
    color: #7ee787;
}

#boot-list > .boot-line.active {
    color: #f4b183;
    text-style: bold;
}

#boot-status {
    color: #58a6ff;
    text-align: center;
    padding: 1 0;
}

#boot-ready {
    color: #7ee787;
    text-align: center;
    text-style: bold;
    padding: 1 0;
    height: 1;
    visibility: hidden;
}

#boot-ready.visible {
    visibility: visible;
}

/* ── Main chat screen ────────────────────────────────────────────────── */

#main-screen {
    layout: vertical;
    background: #0a0a0a;
}

#main-header {
    height: 1;
    background: #141414;
    color: #f4b183;
    text-style: bold;
    padding: 0 2;
    border-bottom: solid #2a2a2a;
}

#main-content {
    layout: horizontal;
    height: 1fr;
}

#chat-column {
    layout: vertical;
    width: 1fr;
    border-right: solid #2a2a2a;
}

#agent-column {
    width: 38;
    layout: vertical;
    background: #0f0f0f;
}

#agent-column.hidden {
    display: none;
}

#chat-log {
    background: #0a0a0a;
    padding: 1 2;
    scrollbar-gutter: stable;
}

#chat-log > * {
    margin-bottom: 1;
}

.chat-user {
    color: #f4b183;
    text-style: bold;
    margin-top: 1;
}

.chat-user .chat-user-arrow {
    color: #f4b183;
    text-style: bold;
}

.chat-agent {
    color: #7ee787;
    text-style: bold;
    margin-top: 1;
}

.chat-stream {
    color: #e6e6e6;
    padding-left: 2;
}

.chat-error {
    color: #ff6b6b;
    background: #1a0f0f;
    border: round #ff6b6b;
    padding: 1 2;
}

.chat-system {
    color: #9a9a9a;
    text-style: italic;
    padding: 1 0;
}

/* ── Thinking box ────────────────────────────────────────────────────── */

ThinkingBox {
    background: #141414;
    border: round #2a2a2a;
    height: auto;
    margin: 1 0;
    padding: 0 1;
}

#thinking-title {
    color: #f4b183;
    text-style: bold;
    height: 1;
    padding: 0 1;
    border-bottom: solid #2a2a2a;
}

.thinking-step {
    height: 1;
    color: #6a6a6a;
    padding: 0 1;
}

.thinking-step.running {
    color: #f4b183;
    text-style: bold;
}

.thinking-step.done {
    color: #7ee787;
}

.thinking-step.pending {
    color: #6a6a6a;
}

.thinking-step .step-icon {
    width: 3;
}

.thinking-step.running .step-icon {
    color: #f4b183;
}

.thinking-step.done .step-icon {
    color: #7ee787;
}

.thinking-step.pending .step-icon {
    color: #6a6a6a;
}

/* ── Agent board ─────────────────────────────────────────────────────── */

AgentBoard {
    background: #0f0f0f;
    border-left: solid #2a2a2a;
    height: 1fr;
    padding: 1 1;
}

#agent-board-title {
    color: #f4b183;
    text-style: bold;
    height: 1;
    padding: 0 1;
    border-bottom: solid #2a2a2a;
    margin-bottom: 1;
}

.agent-row {
    height: 1;
    color: #9a9a9a;
    padding: 0 1;
}

.agent-row.running {
    color: #7ee787;
}

.agent-row.waiting {
    color: #6a6a6a;
}

.agent-row.error {
    color: #ff6b6b;
}

.agent-row .agent-icon {
    width: 3;
}

.agent-row .agent-name {
    width: 1fr;
}

.agent-row .agent-status {
    color: #9a9a9a;
    text-style: bold;
}

.agent-row.running .agent-status {
    color: #7ee787;
}

.agent-row.waiting .agent-status {
    color: #6a6a6a;
}

/* ── Loading indicator (replaces the thinking box for short waits) ──── */

#loading-indicator {
    height: 1;
    color: #f4b183;
    padding: 0 2;
    visibility: hidden;
}

#loading-indicator.visible {
    visibility: visible;
}

#loading-spinner {
    color: #f4b183;
    text-style: bold;
    width: 3;
}

#loading-text {
    color: #f4b183;
}

/* ── Input area ──────────────────────────────────────────────────────── */

#input-area {
    height: auto;
    background: #141414;
    border-top: solid #2a2a2a;
    padding: 0 1;
}

#input-box {
    height: 3;
    background: #141414;
    border: tall #f4b183;
    padding: 0 1;
}

#input-box:focus {
    border: tall #f4b183;
}

#input-box > .input--cursor {
    color: #f4b183;
    background: #f4b183;
    text-style: bold;
}

#input-prefix {
    color: #f4b183;
    text-style: bold;
    width: 3;
    padding: 1 0 0 1;
}

#input-hint {
    color: #6a6a6a;
    height: 1;
    padding: 0 2;
}

/* ── Status bar ──────────────────────────────────────────────────────── */

#status-bar {
    dock: bottom;
    height: 1;
    background: #141414;
    color: #9a9a9a;
    padding: 0 2;
    border-top: solid #2a2a2a;
}

#status-bar > .status-cell {
    padding: 0 2;
    color: #9a9a9a;
}

#status-bar > .status-cell.accent {
    color: #f4b183;
    text-style: bold;
}

#status-bar > .status-cell.success {
    color: #7ee787;
}

#status-bar > .status-cell.info {
    color: #58a6ff;
}

#status-bar > .status-cell.warning {
    color: #e3b341;
}

#status-bar > .status-spacer {
    width: 1fr;
}

/* ── Command palette (modal) ─────────────────────────────────────────── */

#palette-screen {
    align: center middle;
    background: rgba(0, 0, 0, 70%);
}

#palette-container {
    width: 70;
    height: auto;
    max-height: 24;
    background: #141414;
    border: round #f4b183;
    padding: 1 1;
}

#palette-title {
    color: #f4b183;
    text-style: bold;
    height: 1;
    padding: 0 1;
}

#palette-input {
    height: 3;
    background: #0a0a0a;
    border: tall #2a2a2a;
    margin: 1 0;
    padding: 0 1;
}

#palette-list {
    height: auto;
    max-height: 16;
    background: #0a0a0a;
    border: round #2a2a2a;
    padding: 0 1;
}

.palette-item {
    height: 1;
    color: #9a9a9a;
    padding: 0 1;
}

.palette-item.--highlight {
    background: #2a2a2a;
    color: #f4b183;
    text-style: bold;
}

.palette-item .palette-cmd {
    color: #e3b341;
    text-style: bold;
    width: auto;
}

.palette-item .palette-desc {
    color: #9a9a9a;
    padding-left: 2;
}

#palette-hint {
    color: #6a6a6a;
    height: 1;
    padding: 0 1;
    margin-top: 1;
}

/* ── Modal helper ────────────────────────────────────────────────────── */

.help-modal {
    align: center middle;
}

#help-content {
    width: 80;
    height: auto;
    max-height: 80%;
    background: #141414;
    border: round #f4b183;
    padding: 1 2;
}

#help-title {
    color: #f4b183;
    text-style: bold;
    height: 1;
    padding: 0 0 1 0;
    border-bottom: solid #2a2a2a;
    margin-bottom: 1;
}

.help-section-title {
    color: #f4b183;
    text-style: bold;
    padding: 1 0 0 0;
}

.help-row {
    height: 1;
    color: #9a9a9a;
}

.help-row .help-cmd {
    color: #e3b341;
    text-style: bold;
    width: 18;
}

.help-row .help-desc {
    color: #9a9a9a;
}
"""
