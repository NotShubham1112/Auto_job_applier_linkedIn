"""BROWORK Textual CSS — clean professional, black background.

Color rules:
  - Background: pure black #000000 everywhere
  - Text: white #ffffff
  - Primary: blue #3b82f6
  - Accent: red rose #f43f5e
  - All scrollbars: width 1 (thin)
"""


def get_css() -> str:
    return r"""
/* ── Global ────────────────────────────────────────────────────────── */

* {
    scrollbar-size: 1 1;
    scrollbar-color: #3b82f6;
    scrollbar-color-active: #f43f5e;
    scrollbar-color-hover: #ffffff;
    scrollbar-background: #000000;
    scrollbar-background-active: #000000;
    scrollbar-background-hover: #000000;
}

Screen {
    background: #000000;
    color: #ffffff;
    layers: base overlay modal;
}

#app-grid {
    layout: vertical;
    height: 100%;
}

/* ── Boot / Loading screen ────────────────────────────────────────── */

#boot-screen {
    align: center middle;
    background: #000000;
}

#boot-logo {
    width: auto;
    height: auto;
    color: #3b82f6;
    text-style: bold;
}

#boot-tagline {
    color: #ffffff;
    text-align: center;
    padding: 1 0;
}

#boot-version {
    color: #ffffff;
    text-align: center;
    padding: 0 0 1 0;
}

#boot-list {
    width: 50;
    height: auto;
    padding: 1 2;
}

#boot-list > .boot-line {
    height: 1;
    color: #ffffff;
}

#boot-list > .boot-line.done {
    color: #3b82f6;
    text-style: bold;
}

#boot-list > .boot-line.active {
    color: #ffffff;
    text-style: bold;
}

#boot-status {
    color: #ffffff;
    text-align: center;
    padding: 1 0;
}

#boot-ready {
    color: #f43f5e;
    text-align: center;
    text-style: bold;
    padding: 1 0;
    height: 1;
    visibility: hidden;
}

#boot-ready.visible {
    visibility: visible;
}

/* ── Main chat screen ─────────────────────────────────────────────── */

#main-screen {
    layout: vertical;
    background: #000000;
}

#main-header {
    height: 1;
    background: #000000;
    color: #ffffff;
    text-style: bold;
    padding: 0 2;
    border-bottom: solid #3b82f6;
}

#main-content {
    layout: horizontal;
    height: 1fr;
    background: #000000;
}

#chat-column {
    layout: vertical;
    width: 1fr;
    background: #000000;
    border-right: solid #3b82f6;
}

#agent-column {
    width: 38;
    layout: vertical;
    background: #000000;
    border-left: solid #3b82f6;
}

#agent-column.hidden {
    display: none;
}

#chat-log {
    background: #000000;
    color: #ffffff;
    padding: 1 2;
    scrollbar-gutter: stable;
    scrollbar-size: 1 1;
}

#chat-log > * {
    margin-bottom: 1;
}

.chat-user {
    color: #ffffff;
    text-style: bold;
    margin-top: 1;
}

.chat-user .chat-user-arrow {
    color: #f43f5e;
    text-style: bold;
}

.chat-agent {
    color: #3b82f6;
    text-style: bold;
    margin-top: 1;
}

.chat-stream {
    color: #ffffff;
    padding-left: 2;
}

.chat-error {
    color: #f43f5e;
    background: #000000;
    border: round #f43f5e;
    padding: 1 2;
}

.chat-system {
    color: #ffffff;
    padding: 1 0;
}

/* ── Thinking box ─────────────────────────────────────────────────── */

ThinkingBox {
    background: #000000;
    border: round #3b82f6;
    height: auto;
    margin: 1 0;
    padding: 0 1;
}

#thinking-title {
    color: #3b82f6;
    text-style: bold;
    height: 1;
    padding: 0 1;
    border-bottom: solid #3b82f6;
}

.thinking-step {
    height: 1;
    color: #ffffff;
    padding: 0 1;
}

.thinking-step.running {
    color: #ffffff;
    text-style: bold;
}

.thinking-step.done {
    color: #3b82f6;
}

.thinking-step.pending {
    color: #ffffff;
}

.thinking-step .step-icon {
    width: 3;
}

.thinking-step.running .step-icon {
    color: #f43f5e;
}

.thinking-step.done .step-icon {
    color: #3b82f6;
}

.thinking-step.pending .step-icon {
    color: #ffffff;
}

/* ── Agent board ──────────────────────────────────────────────────── */

AgentBoard {
    background: #000000;
    height: 1fr;
    padding: 1 1;
}

#agent-board-title {
    color: #ffffff;
    text-style: bold;
    height: 1;
    padding: 0 1;
    border-bottom: solid #3b82f6;
    margin-bottom: 1;
}

.agent-row {
    height: 1;
    color: #ffffff;
    padding: 0 1;
}

.agent-row.running {
    color: #3b82f6;
}

.agent-row.waiting {
    color: #ffffff;
}

.agent-row.error {
    color: #f43f5e;
}

.agent-row .agent-icon {
    width: 3;
}

.agent-row .agent-name {
    width: 1fr;
}

.agent-row .agent-status {
    color: #ffffff;
    text-style: bold;
}

.agent-row.running .agent-status {
    color: #3b82f6;
}

.agent-row.waiting .agent-status {
    color: #ffffff;
}

.agent-row.done .agent-status {
    color: #ffffff;
}

/* ── Loading indicator ────────────────────────────────────────────── */

#loading-indicator {
    height: 1;
    color: #3b82f6;
    padding: 0 2;
    visibility: hidden;
}

#loading-indicator.visible {
    visibility: visible;
}

#loading-spinner {
    color: #f43f5e;
    text-style: bold;
    width: 3;
}

#loading-text {
    color: #3b82f6;
}

/* ── Input area ───────────────────────────────────────────────────── */

#input-area {
    height: auto;
    background: #000000;
    border-top: solid #3b82f6;
    padding: 0 1;
}

#input-box {
    height: 3;
    background: #000000;
    color: #ffffff;
    border: tall #3b82f6;
    padding: 0 1;
}

#input-box:focus {
    border: tall #f43f5e;
}

#input-box > .input--cursor {
    color: #f43f5e;
    background: #f43f5e;
    text-style: bold;
}

#input-box > .input--placeholder {
    color: #ffffff;
    text-style: italic;
}

#input-prefix {
    color: #f43f5e;
    text-style: bold;
    width: 3;
    padding: 1 0 0 1;
}

#input-hint {
    color: #ffffff;
    height: 1;
    padding: 0 2;
}

/* ── Status bar ───────────────────────────────────────────────────── */

#status-bar {
    dock: bottom;
    height: 1;
    background: #000000;
    color: #ffffff;
    padding: 0 2;
    border-top: solid #3b82f6;
}

#status-bar > .status-cell {
    padding: 0 2;
    color: #ffffff;
}

#status-bar > .status-cell.accent {
    color: #f43f5e;
    text-style: bold;
}

#status-bar > .status-cell.success {
    color: #3b82f6;
}

#status-bar > .status-cell.info {
    color: #3b82f6;
}

#status-bar > .status-cell.warning {
    color: #f43f5e;
}

#status-bar > .status-spacer {
    width: 1fr;
}

/* ── Command palette (modal) ──────────────────────────────────────── */

#palette-screen {
    align: center middle;
    background: #000000;
}

#palette-container {
    width: 70;
    height: auto;
    max-height: 24;
    background: #000000;
    border: round #3b82f6;
    padding: 1 1;
}

#palette-title {
    color: #3b82f6;
    text-style: bold;
    height: 1;
    padding: 0 1;
}

#palette-input {
    height: 3;
    background: #000000;
    color: #ffffff;
    border: tall #3b82f6;
    margin: 1 0;
    padding: 0 1;
}

#palette-input:focus {
    border: tall #f43f5e;
}

#palette-list {
    height: auto;
    max-height: 16;
    background: #000000;
    border: round #3b82f6;
    padding: 0 1;
    scrollbar-size: 1 1;
}

.palette-item {
    height: 1;
    color: #ffffff;
    padding: 0 1;
}

.palette-item.--highlight {
    background: #3b82f6;
    color: #ffffff;
    text-style: bold;
}

.palette-item .palette-cmd {
    color: #f43f5e;
    text-style: bold;
    width: auto;
}

.palette-item .palette-desc {
    color: #ffffff;
    padding-left: 2;
}

#palette-hint {
    color: #ffffff;
    height: 1;
    padding: 0 1;
    margin-top: 1;
}

/* ── Help modal ───────────────────────────────────────────────────── */

.help-modal {
    align: center middle;
}

#help-content {
    width: 80;
    height: auto;
    max-height: 80%;
    background: #000000;
    border: round #3b82f6;
    padding: 1 2;
}

#help-title {
    color: #ffffff;
    text-style: bold;
    height: 1;
    padding: 0 0 1 0;
    border-bottom: solid #3b82f6;
    margin-bottom: 1;
}

.help-section-title {
    color: #3b82f6;
    text-style: bold;
    padding: 1 0 0 0;
}

.help-row {
    height: 1;
    color: #ffffff;
}

.help-row .help-cmd {
    color: #f43f5e;
    text-style: bold;
    width: 18;
}

.help-row .help-desc {
    color: #ffffff;
}

#help-hint {
    color: #ffffff;
    text-align: center;
    padding: 1 0 0 0;
}
"""
