"""BROWORK Textual CSS — minimal aesthetic.

Design principles:
  - No borders, no box-drawing, no decorative elements
  - Whitespace and alignment only
  - Typography hierarchy via color and weight
  - Pure black background everywhere
  - Blue for primary/brand, red-rose for accent/alerts
  - Responsive to terminal size
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

/* ── Boot screen ───────────────────────────────────────────────────── */

BootScreen {
    background: #000000;
    align: center middle;
}

#boot-container {
    width: auto;
    height: auto;
    align: center middle;
}

#boot-matrix {
    width: 100%;
    height: 100%;
    color: #3b82f6;
    background: #000000;
}

#boot-logo {
    color: #3b82f6;
    text-style: bold;
    width: auto;
    content-align: center middle;
}

#boot-tagline {
    color: #ffffff;
    text-align: center;
    padding: 1 0 0 0;
}

#boot-version {
    color: #666666;
    text-align: center;
    padding: 0 0 1 0;
}

#boot-list {
    width: auto;
    height: auto;
    padding: 1 0;
}

#boot-status {
    color: #666666;
    text-align: center;
    padding: 1 0 0 0;
}

#boot-ready {
    color: #f43f5e;
    text-align: center;
    text-style: bold;
    padding: 1 0 0 0;
    height: 1;
    visibility: hidden;
}

#boot-ready.visible {
    visibility: visible;
}

/* ── Main screen ───────────────────────────────────────────────────── */

MainScreen {
    layout: vertical;
    background: #000000;
}

#main-header {
    height: 1;
    background: #000000;
    color: #666666;
    padding: 0 2;
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
}

#thinking-host {
    height: auto;
    padding: 0 2;
}

#thinking-host.hidden {
    display: none;
}

#log-container {
    height: 1fr;
    background: #000000;
    scrollbar-size: 1 1;
}

#loading-indicator {
    height: 1;
    color: #666666;
    padding: 0 4;
    visibility: hidden;
}

#loading-indicator.visible {
    visibility: visible;
}

#loading-spinner {
    color: #3b82f6;
    width: 3;
}

#loading-text {
    color: #666666;
}

#agent-column {
    width: 38;
    background: #000000;
}

#agent-column.hidden {
    display: none;
}

/* ── Input area ────────────────────────────────────────────────────── */

#input-area {
    height: auto;
    background: #000000;
    padding: 1 2 0 2;
}

#input-row {
    height: 3;
    background: #000000;
}

#input-box {
    height: 3;
    background: #000000;
    color: #ffffff;
    padding: 0 1;
}

#input-box:focus {
    color: #ffffff;
}

#input-box > .input--cursor {
    color: #f43f5e;
    background: #f43f5e;
    text-style: bold;
}

#input-box > .input--placeholder {
    color: #444444;
}

#input-prefix {
    color: #3b82f6;
    text-style: bold;
    width: 3;
    padding: 1 0 0 0;
}

#input-hint {
    color: #444444;
    height: 1;
    padding: 0 0;
}

/* ── Chat message styles ───────────────────────────────────────────── */

.chat-user {
    color: #ffffff;
    text-style: bold;
    margin-top: 1;
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
    padding: 0 0;
}

.chat-system {
    color: #666666;
    padding: 0 0;
}

/* ── Thinking box ──────────────────────────────────────────────────── */

ThinkingBox {
    background: #000000;
    height: auto;
    margin: 0 0;
    padding: 0 0;
}

#thinking-title {
    color: #666666;
    height: 1;
    padding: 0 0;
}

.thinking-step {
    height: 1;
    color: #666666;
    padding: 0 0;
}

.thinking-step.running {
    color: #ffffff;
    text-style: bold;
}

.thinking-step.done {
    color: #3b82f6;
}

.thinking-step.pending {
    color: #666666;
}

.thinking-step.error {
    color: #f43f5e;
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
    color: #444444;
}

/* ── Agent board ───────────────────────────────────────────────────── */

AgentBoard {
    background: #000000;
    height: 1fr;
    padding: 1 1;
}

#agent-board-title {
    color: #666666;
    height: 1;
    padding: 0 0;
    margin-bottom: 1;
}

.agent-row {
    height: 1;
    color: #666666;
    padding: 0 0;
}

.agent-row.running {
    color: #3b82f6;
}

.agent-row.waiting {
    color: #666666;
}

.agent-row.done {
    color: #666666;
}

.agent-row.error {
    color: #f43f5e;
}

.agent-row.pending {
    color: #666666;
}

.agent-row .agent-icon {
    width: 3;
}

.agent-row .agent-name {
    width: 1fr;
}

.agent-row .agent-status {
    color: #666666;
    text-style: bold;
}

.agent-row.running .agent-status {
    color: #3b82f6;
}

.agent-row.waiting .agent-status {
    color: #666666;
}

.agent-row.done .agent-status {
    color: #666666;
}

/* ── Status bar ────────────────────────────────────────────────────── */

#status-bar {
    dock: bottom;
    height: 1;
    background: #000000;
    color: #666666;
    padding: 0 2;
}

#status-bar > .status-cell {
    padding: 0 1;
    color: #666666;
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

/* ── Command palette (modal) ───────────────────────────────────────── */

CommandPalette {
    align: center middle;
    background: #000000EE;
}

#palette-container {
    width: 70;
    height: auto;
    max-height: 24;
    background: #000000;
    padding: 1 0;
}

#palette-title {
    color: #666666;
    height: 1;
    padding: 0 2;
}

#palette-input {
    height: 3;
    background: #000000;
    color: #ffffff;
    margin: 0 2;
    padding: 0 1;
}

#palette-input:focus {
    color: #ffffff;
}

#palette-input > .input--placeholder {
    color: #444444;
}

#palette-list {
    height: auto;
    max-height: 16;
    background: #000000;
    padding: 0 0;
    scrollbar-size: 1 1;
}

.palette-item {
    height: 1;
    color: #666666;
    padding: 0 2;
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
    color: #666666;
    padding-left: 2;
}

#palette-hint {
    color: #444444;
    height: 1;
    padding: 0 2;
    margin-top: 1;
}

/* ── Help modal ────────────────────────────────────────────────────── */

HelpScreen {
    align: center middle;
    background: #000000EE;
}

#help-content {
    width: 80;
    height: auto;
    max-height: 80%;
    background: #000000;
    padding: 1 2;
}

#help-title {
    color: #ffffff;
    text-style: bold;
    height: 1;
    padding: 0 0 1 0;
    margin-bottom: 1;
}

#help-scroll {
    height: auto;
    max-height: 50;
    scrollbar-size: 1 1;
}

.help-section-title {
    color: #3b82f6;
    text-style: bold;
    padding: 1 0 0 0;
}

.help-row {
    height: 1;
    color: #666666;
}

.help-row .help-cmd {
    color: #f43f5e;
    text-style: bold;
    width: 18;
}

.help-row .help-desc {
    color: #666666;
}

#help-hint {
    color: #444444;
    text-align: center;
    padding: 1 0 0 0;
}
"""
