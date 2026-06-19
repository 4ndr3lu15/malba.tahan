"""Loading hand-drawn ascii/unicode art from ``assets/art/``.

Art is stored as plain ``.txt`` files (one per background) so authoring is just
"draw a picture in a text file and reference it by name from a chapter". Missing
art degrades gracefully to an empty panel rather than crashing a play session.
"""

from __future__ import annotations

from functools import lru_cache
from importlib import resources


@lru_cache(maxsize=None)
def load_art(name: str, *, package: str = "malba_tahan") -> str:
    """Return the art named ``name`` (without extension), or "" if absent."""
    if not name:
        return ""
    try:
        return resources.files(package).joinpath(f"assets/art/{name}.txt").read_text("utf-8").rstrip("\n")
    except (FileNotFoundError, NotADirectoryError):
        return ""
