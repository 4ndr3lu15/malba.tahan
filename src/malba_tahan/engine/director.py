"""The director: walks a scene's beats and drives the stage.

Runs as a Textual worker so it can ``await`` player input and puzzle results
inline. The branching *math* lives in :mod:`malba_tahan.engine.story`
(``resolve_branch``/``index_of_label``); this module only sequences the calls and
talks to the :class:`~malba_tahan.engine.novel_screen.NovelScreen`.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from . import story
from .assets import load_art
from .story import Art, Choice, End, Goto, Label, Narration, Puzzle, Say, Scene

if TYPE_CHECKING:
    from .novel_screen import NovelScreen


@dataclass(frozen=True)
class PuzzleResult:
    """What a bespoke puzzle screen hands back to the story.

    Puzzles dismiss with one of these; the director branches on :attr:`won`.
    ``detail`` is free-form so a puzzle can pass a flavour string back into the
    narration later if we want it.
    """

    won: bool
    detail: str = ""


class Director:
    def __init__(self, screen: "NovelScreen", scene: Scene) -> None:
        self.screen = screen
        self.scene = scene

    async def run(self) -> None:
        i: int | None = 0
        while i is not None and 0 <= i < len(self.scene.beats):
            i = await self._play(self.scene.beats[i], i)
        self.screen.on_story_end()

    async def _play(self, beat, index: int) -> int | None:
        if isinstance(beat, Narration):
            self._maybe_art(beat.art)
            await self.screen.show_text(None, "#A0A0A0", beat.text, beat.speed)
            return story.next_index(self.scene, index)

        if isinstance(beat, Say):
            self._maybe_art(beat.art)
            who = self.scene.character(beat.speaker)
            await self.screen.show_text(who.name, who.color, beat.text, beat.speed)
            return story.next_index(self.scene, index)

        if isinstance(beat, Art):
            self.screen.set_art(load_art(beat.art), transition=beat.transition)
            return story.next_index(self.scene, index)

        if isinstance(beat, Choice):
            goto = await self.screen.ask_choice(beat.prompt, beat.options)
            return self.scene.index_of_label(goto)

        if isinstance(beat, Puzzle):
            result = await self.screen.run_puzzle(beat.id)
            label = beat.on_win if result.won else beat.on_lose
            return story.resolve_branch(self.scene, label, index)

        if isinstance(beat, Label):
            return story.next_index(self.scene, index)

        if isinstance(beat, Goto):
            return self.scene.index_of_label(beat.target)

        if isinstance(beat, End):
            await self.screen.show_end(beat.text)
            return None

        # unknown beat: skip rather than crash a play session.
        return story.next_index(self.scene, index)

    def _maybe_art(self, art: str | None) -> None:
        if art:
            self.screen.set_art(load_art(art))
