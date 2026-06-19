"""Animated Textual widgets that make the stage feel alive.

Each widget keeps its *timing math* in :mod:`malba_tahan.engine.anim` and only
applies the results here — to Textual timers (``set_interval``) and property
animations (``styles.animate``). That split is what lets the engine's behaviour
be unit-tested without spinning up a terminal.
"""

from __future__ import annotations

import random

from rich.text import Text
from textual.widgets import Static

from . import anim

# how often the typewriter / ambient timers tick, in seconds.
_TICK = 1.0 / 30.0


class AsciiArtPanel(Static):
    """A background panel that cross-fades when its art changes."""

    def show(self, art: str, *, transition: str = "fade") -> None:
        self.update(Text.from_markup(art) if "[" in art else art)
        if transition == "fade":
            self.styles.opacity = 0.0
            self.styles.animate("opacity", value=1.0, duration=0.5)
        else:
            self.styles.opacity = 1.0


class NamePlate(Static):
    """Shows the current speaker's name, popping in when the speaker changes."""

    def __init__(self) -> None:
        super().__init__("")
        self._current: str | None = None

    def set_speaker(self, name: str, color: str) -> None:
        if name == self._current:
            return
        self._current = name
        self.update(Text(f" {name} ", style=f"bold {color}"))
        # a small pop: appear from transparent so the eye catches the new speaker.
        self.styles.opacity = 0.0
        self.styles.animate("opacity", value=1.0, duration=0.25)

    def clear_speaker(self) -> None:
        self._current = None
        self.update("")


class TypewriterText(Static):
    """Reveals text one character at a time, then waits to be advanced.

    Press-to-skip is handled by the screen: while :attr:`is_revealing` is true a
    press calls :meth:`fast_forward`; once revealed, a press advances the beat.
    """

    def __init__(self) -> None:
        super().__init__("")
        self._full = ""
        self._elapsed = 0.0
        self._cps = anim.DEFAULT_CPS
        self._timer = None

    @property
    def is_revealing(self) -> bool:
        return self._timer is not None

    def reveal(self, text: str, *, cps: float | None = None) -> None:
        self._stop()
        self._full = text
        self._elapsed = 0.0
        self._cps = cps if cps is not None else anim.DEFAULT_CPS
        self.update("")
        if anim.is_typewriter_done(0.0, len(text), self._cps):
            self._finish()
        else:
            self._timer = self.set_interval(_TICK, self._tick)

    def fast_forward(self) -> None:
        if self.is_revealing:
            self._finish()

    def _tick(self) -> None:
        self._elapsed += _TICK
        n = anim.typewriter_index(self._elapsed, len(self._full), self._cps)
        self.update(self._full[:n])
        if anim.is_typewriter_done(self._elapsed, len(self._full), self._cps):
            self._finish()

    def _finish(self) -> None:
        self._stop()
        self.update(self._full)

    def _stop(self) -> None:
        if self._timer is not None:
            self._timer.stop()
            self._timer = None


# small palette of ambient glyphs for the desert night sky.
_STARS = "·.✦*•˙"


class AmbientLayer(Static):
    """A subtle drifting star/sand field for title and interstitial screens.

    Purely decorative: a handful of faint glyphs drift leftward and wrap around,
    giving the otherwise-static title a sense of a living desert night.
    """

    def __init__(self, *, density: int = 24, color: str = "#3b4a63", **kwargs) -> None:
        super().__init__("", **kwargs)
        self._density = density
        self._color = color
        self._stars: list[list[float]] = []  # [x, y, glyph_index]
        self._timer = None
        self._rng = random.Random(7)

    def on_mount(self) -> None:
        self._seed()
        self._timer = self.set_interval(_TICK * 3, self._drift)

    def on_resize(self) -> None:
        self._seed()

    def _seed(self) -> None:
        w, h = self.size.width or 80, self.size.height or 24
        self._stars = [
            [self._rng.uniform(0, w), self._rng.randrange(max(h, 1)), self._rng.randrange(len(_STARS))]
            for _ in range(self._density)
        ]
        self._paint()

    def _drift(self) -> None:
        w = self.size.width or 80
        for star in self._stars:
            star[0] -= 0.5
            if star[0] < 0:
                star[0] += w
        self._paint()

    def _paint(self) -> None:
        w, h = self.size.width or 80, self.size.height or 24
        grid = [[" "] * w for _ in range(h)]
        for x, y, gi in self._stars:
            xi, yi = int(x), int(y)
            if 0 <= xi < w and 0 <= yi < h:
                grid[yi][xi] = _STARS[int(gi)]
        body = "\n".join("".join(row) for row in grid)
        self.update(Text(body, style=self._color))
