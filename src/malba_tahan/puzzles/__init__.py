"""Bespoke puzzle screens, registered by id.

Each puzzle is a *hand-crafted* piece of game design — not an instance of some
generic template. The only contract the engine imposes is: a puzzle is a Textual
``Screen`` that, when finished, dismisses with a
:class:`~malba_tahan.engine.director.PuzzleResult`. The director branches the
story on ``result.won``.

To add a puzzle: build its screen module, then register a factory here under a
short id, and reference that id from a chapter's ``puzzle:`` beat. The
``/new-puzzle`` skill scaffolds the boilerplate.
"""

from __future__ import annotations

from typing import Callable

from textual.screen import Screen

from .balance import BalancePuzzleScreen

# id -> zero-arg factory that builds a fresh puzzle screen.
REGISTRY: dict[str, Callable[[], Screen]] = {
    "balance": BalancePuzzleScreen,
}


def puzzle_ids() -> set[str]:
    """Ids known to the registry — used to validate chapter files at load time."""
    return set(REGISTRY)


def make_puzzle(puzzle_id: str) -> Screen:
    """Build the puzzle screen registered under ``puzzle_id``."""
    try:
        return REGISTRY[puzzle_id]()
    except KeyError as exc:
        raise KeyError(f"unknown puzzle id: {puzzle_id!r} (known: {sorted(REGISTRY)})") from exc
