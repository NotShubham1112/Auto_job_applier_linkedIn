"""Dynamic loading messages that rotate while work is happening.

The OpenCode/Vibe-Code style: instead of "Thinking...", show a sequence
of status messages that change every ~700ms while the agent works.
"""

from __future__ import annotations

import random
from typing import Iterator

from cli.styles.palette import LOADING_MESSAGES, SPINNER_FRAMES


def rotating_messages(
    interval: int = 700,
    shuffle: bool = True,
    seed: int | None = None,
) -> Iterator[str]:
    """Yield loading messages forever, switching every `interval` ms.

    The caller is expected to honor the interval (e.g. by sleeping
    between calls). This generator simply hands out the next string.

    Args:
        interval: Suggested interval (ms) between rotations. Returned
            alongside each message via a side-channel would require a
            custom object, so the caller reads the value from here.
        shuffle: If True, shuffle the message list once at the start.
        seed: Optional seed for reproducible shuffles (mostly for tests).

    Yields:
        The next loading message.
    """
    messages = list(LOADING_MESSAGES)
    if shuffle:
        rng = random.Random(seed)
        rng.shuffle(messages)

    i = 0
    while True:
        yield messages[i % len(messages)]
        i += 1


def spinner_frames() -> Iterator[str]:
    """Yield the standard spinner glyphs in order, forever."""
    i = 0
    while True:
        yield SPINNER_FRAMES[i % len(SPINNER_FRAMES)]
        i += 1


def progress_frame(percent: int) -> str:
    """Return a textual progress bar (opencode-style) for a percent.

    Renders a 10-cell bar like:
        [████████  ] 80%
    """
    percent = max(0, min(100, percent))
    filled = round(percent / 10)
    empty = 10 - filled
    bar = "\u2588" * filled + "\u2591" * empty
    return f"[{bar}] {percent}%"


def scan_line(width: int = 32) -> str:
    """Return a single-frame scan line of `width` characters."""
    chars = [
        "\u2581", "\u2582", "\u2583", "\u2584",
        "\u2585", "\u2586", "\u2587", "\u2588",
    ]
    if width <= 0:
        return ""
    # Build an asymmetric scan effect
    half = width // 2
    out = []
    for i in range(half):
        out.append(chars[i % len(chars)])
    for i in range(width - half):
        out.append(chars[(len(chars) - 1 - i) % len(chars)])
    return "".join(out)
