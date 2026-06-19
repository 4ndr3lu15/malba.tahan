---
name: new-puzzle
description: Scaffold a new bespoke puzzle screen for the malba tahan visual novel and register it. Use when adding a hand-crafted puzzle from the book.
---

# new puzzle

Puzzles are **artisanal**, not instances of a generic template — each one is
designed by hand to fit its moment in the story. This skill only removes the
boilerplate (the screen shell + registration); the actual design is done with
the user.

## the only contract

A puzzle is a Textual `Screen` (usually `ModalScreen`) that, when finished,
`dismiss(...)`es with a `PuzzleResult(won=..., detail="...")` from
`malba_tahan.engine.director`. The director branches the story on `result.won`.

Reuse the palette (gold `#D4AF37`, navy `#0b1320`/`#101c30`) and lowercase prose.
Keep any pure rules in a separate UI-free module (like `game.py`) so they can be
unit-tested — that's how the balance puzzle is structured; follow it.

## steps

1. Create `src/malba_tahan/puzzles/<name>.py` from the template below.
2. Register it in `src/malba_tahan/puzzles/__init__.py`:
   ```python
   from .<name> import <Name>PuzzleScreen
   REGISTRY = {
       "balance": BalancePuzzleScreen,
       "<id>": <Name>PuzzleScreen,
   }
   ```
3. Reference `<id>` from a chapter's `puzzle:` beat (see `/new-chapter`).
4. If there are pure rules, add `tests/test_<name>.py`.
5. Verify with `/play` (the puzzle needs to be reachable from a chapter, or
   instantiate `<Name>PuzzleScreen` directly in a pilot test).

## template

```python
"""<one-line description of the puzzle and its place in the book>."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Button, Footer, Static

from ..engine.director import PuzzleResult

GOLD = "#D4AF37"


class <Name>PuzzleScreen(ModalScreen[PuzzleResult]):
    CSS = """
    <Name>PuzzleScreen { background: #0b1320; color: #E0E0E0; align: center middle; }
    #title { width: 100%; text-align: center; text-style: bold; color: #D4AF37; }
    """

    def compose(self) -> ComposeResult:
        yield Static("the trial of ...", id="title")
        # ... bespoke, hand-crafted UI for this puzzle ...
        yield Button("submit", variant="success", id="submit")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "submit":
            won = self._check()           # your win condition
            self.dismiss(PuzzleResult(won=won, detail=""))

    def _check(self) -> bool:
        raise NotImplementedError
```

When showing a win/lose flourish before handing back, push a small overlay screen
and dismiss from its callback as a **statement** (not `lambda: self.dismiss(...)`,
which Textual would try to await). See `puzzles/balance.py` `_make_guess`.
