"""Matrix rain animation for the boot screen.

Lightweight, non-blocking matrix-style falling characters.
Uses a small set of columns and simple physics for smooth animation
without blocking the event loop.

The animation runs for a fixed duration, then fades out cleanly
into the boot sequence.
"""

from __future__ import annotations

import asyncio
import random
from typing import Iterator

from cli.styles.palette import MATRIX_CHARS, PALETTE


class MatrixColumn:
    """A single falling column of characters."""

    __slots__ = ("x", "y", "speed", "chars", "length", "active")

    def __init__(self, x: int, height: int) -> None:
        self.x = x
        self.y = random.randint(-height, 0)
        self.speed = random.uniform(0.6, 1.4)
        self.length = random.randint(4, min(12, height))
        self.active = True
        self.chars: list[str] = [
            random.choice(MATRIX_CHARS) for _ in range(self.length)
        ]


class MatrixRain:
    """Lightweight matrix rain renderer for Textual Static widgets.

    Usage:
        rain = MatrixRain(width, height)
        for frame in rain.frames(duration_seconds=1.5):
            static_widget.update(frame)

    The animation is non-blocking: each frame is a string that can
    be rendered by a Textual Static widget. The caller controls the
    timing via asyncio.sleep().
    """

    def __init__(self, width: int, height: int, density: float = 0.3) -> None:
        self.width = width
        self.height = height
        self.density = density
        self.columns: list[MatrixColumn] = []
        self._initialize_columns()

    def _initialize_columns(self) -> None:
        """Create columns at random positions."""
        num_columns = max(1, int(self.width * self.density))
        positions = random.sample(
            range(self.width), min(num_columns, self.width)
        )
        for x in positions:
            self.columns.append(MatrixColumn(x, self.height))

    def _render_frame(self) -> str:
        """Render the current state as a string."""
        grid = [[" " for _ in range(self.width)] for _ in range(self.height)]

        for col in self.columns:
            if not col.active:
                continue
            for i in range(col.length):
                y = int(col.y) + i
                if 0 <= y < self.height and 0 <= col.x < self.width:
                    # Head character is brightest, tail fades
                    if i == col.length - 1:
                        grid[y][col.x] = col.chars[i]
                    else:
                        grid[y][col.x] = col.chars[i]

        lines = ["".join(row) for row in grid]
        return "\n".join(lines)

    def _advance(self, dt: float) -> None:
        """Advance all columns by dt seconds."""
        for col in self.columns:
            col.y += col.speed * dt * 8
            # Recycle column when it goes off screen
            if col.y - col.length > self.height:
                col.y = random.randint(-self.height // 2, 0)
                col.speed = random.uniform(0.6, 1.4)
                col.chars = [
                    random.choice(MATRIX_CHARS) for _ in range(col.length)
                ]

    async def frames(
        self,
        duration: float = 1.5,
        fps: int = 20,
        fade: bool = True,
    ) -> Iterator[str]:
        """Yield rendered frames for the given duration.

        Args:
            duration: Total animation time in seconds.
            fps: Frames per second (lower = less CPU).
            fade: If True, fade out in the last 0.3s.

        Yields:
            A string for each frame, suitable for Static.update().
        """
        frame_time = 1.0 / fps
        elapsed = 0.0
        fade_start = max(0, duration - 0.3)

        while elapsed < duration:
            self._advance(frame_time)
            frame = self._render_frame()

            # Simple fade: reduce character density near the end
            if fade and elapsed > fade_start:
                progress = (elapsed - fade_start) / (duration - fade_start)
                frame = self._apply_fade(frame, progress)

            yield frame
            elapsed += frame_time
            await asyncio.sleep(frame_time)

    def _apply_fade(self, frame: str, progress: float) -> str:
        """Reduce character density based on fade progress (0..1)."""
        lines = frame.split("\n")
        result = []
        for line in lines:
            new_line = []
            for ch in line:
                if ch != " " and random.random() < progress * 0.7:
                    new_line.append(" ")
                else:
                    new_line.append(ch)
            result.append("".join(new_line))
        return "\n".join(result)
