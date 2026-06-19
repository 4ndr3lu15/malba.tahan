"""The visual-novel stage: a background panel above a dialogue box.

This is the *view* the director talks to. It exposes a small async vocabulary —
``show_text``, ``ask_choice``, ``run_puzzle``, ``show_end`` — and handles the
press-to-skip / press-to-advance dance so the director can stay declarative.
"""

from __future__ import annotations

import asyncio
from typing import Callable

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Static

from .director import Director, PuzzleResult
from .story import ChoiceOption, Scene
from .widgets import AsciiArtPanel, NamePlate, TypewriterText

PuzzleFactory = Callable[[str], Screen]


class Hint(Static):
    """The faint 'press [space]' prompt at the corner of the dialogue box."""

    def __init__(self) -> None:
        super().__init__("press [space] to continue", id="hint")


class NovelScreen(Screen[None]):
    """Plays one :class:`~malba_tahan.engine.story.Scene` to completion."""

    CSS = """
    NovelScreen { background: #0b1320; }
    #stage-art {
        width: 100%;
        height: 1fr;
        content-align: center middle;
        color: #D4AF37;
        padding: 1 2;
    }
    #dialogue {
        dock: bottom;
        width: 100%;
        height: auto;
        min-height: 9;
        background: #101c30;
        border-top: thick #D4AF37;
        padding: 1 3;
    }
    #nameplate { width: auto; height: 1; }
    #line {
        width: 100%;
        height: auto;
        min-height: 4;
        color: #E8E8E8;
        padding: 1 0 0 0;
    }
    #hint {
        width: 100%;
        height: 1;
        text-align: right;
        color: #5b6a83;
        text-style: italic;
    }
    #choices {
        dock: bottom;
        width: 100%;
        height: auto;
        background: #101c30;
        border-top: thick #D4AF37;
        padding: 1 3;
        display: none;
    }
    #choices Button { width: 100%; margin: 0 0 1 0; }
    """

    BINDINGS = [
        ("space", "advance", "continue"),
        ("enter", "advance", "continue"),
        ("q", "quit", "quit"),
    ]

    def __init__(self, scene: Scene, puzzle_factory: PuzzleFactory) -> None:
        super().__init__()
        self.scene = scene
        self._puzzle_factory = puzzle_factory
        self._advance = asyncio.Event()
        self._choice_future: asyncio.Future[str] | None = None
        self._choice_options: list[ChoiceOption] = []
        self._director = Director(self, scene)

    # -- layout -------------------------------------------------------------
    def compose(self) -> ComposeResult:
        yield AsciiArtPanel("", id="stage-art")
        with Vertical(id="dialogue"):
            yield NamePlate()
            yield TypewriterText()
            yield Hint()
        yield Vertical(id="choices")
        yield Footer()

    def on_mount(self) -> None:
        self.sub_title = self.scene.title
        self.run_worker(self._director.run(), exclusive=True)

    # -- convenience handles ------------------------------------------------
    @property
    def _art(self) -> AsciiArtPanel:
        return self.query_one("#stage-art", AsciiArtPanel)

    @property
    def _nameplate(self) -> NamePlate:
        return self.query_one(NamePlate)

    @property
    def _line(self) -> TypewriterText:
        return self.query_one(TypewriterText)

    @property
    def _hint(self) -> Hint:
        return self.query_one(Hint)

    @property
    def _choices(self) -> Vertical:
        return self.query_one("#choices", Vertical)

    # -- director-facing vocabulary -----------------------------------------
    def set_art(self, art: str, *, transition: str = "fade") -> None:
        self._art.show(art, transition=transition)

    async def show_text(
        self, name: str | None, color: str, text: str, speed: float | None
    ) -> None:
        self._choices.display = False
        if name is None:
            self._nameplate.clear_speaker()
        else:
            self._nameplate.set_speaker(name, color)
        self._hint.update("press [space] to continue")
        self._hint.display = True
        self._line.reveal(text, cps=speed)
        await self._wait_advance()

    async def show_end(self, text: str | None) -> None:
        self._nameplate.clear_speaker()
        self._hint.update("press [space] to leave")
        self._hint.display = True
        self._line.reveal(text or "— end of the prologue —")
        await self._wait_advance()

    async def ask_choice(self, prompt: str, options: list[ChoiceOption]) -> str:
        self._nameplate.clear_speaker()
        self._line.reveal(prompt, cps=0)  # show the prompt instantly
        self._hint.display = False
        await self._choices.remove_children()
        self._choice_options = options
        self._choice_future = asyncio.get_event_loop().create_future()
        for idx, opt in enumerate(options):
            await self._choices.mount(Button(f"{idx + 1}. {opt.text}", id=f"choice-{idx}"))
        self._choices.display = True
        try:
            return await self._choice_future
        finally:
            self._choices.display = False
            self._choice_future = None

    async def run_puzzle(self, puzzle_id: str) -> PuzzleResult:
        result = await self.app.push_screen_wait(self._puzzle_factory(puzzle_id))
        if not isinstance(result, PuzzleResult):  # defensive: treat anything truthy as a win
            result = PuzzleResult(won=bool(result))
        return result

    def on_story_end(self) -> None:
        self.dismiss(None)

    # -- input --------------------------------------------------------------
    def action_advance(self) -> None:
        if self._choices.display:
            return
        if self._line.is_revealing:
            self._line.fast_forward()
        else:
            self._advance.set()

    async def _wait_advance(self) -> None:
        self._advance.clear()
        await self._advance.wait()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        bid = event.button.id or ""
        if bid.startswith("choice-") and self._choice_future is not None:
            idx = int(bid.removeprefix("choice-"))
            self._choice_future.set_result(self._choice_options[idx].goto)

    def on_key(self, event) -> None:
        # number keys pick a choice when the choice panel is open.
        if self._choice_future is None or self._choice_future.done():
            return
        if event.character and event.character.isdigit():
            idx = int(event.character) - 1
            if 0 <= idx < len(self._choice_options):
                self._choice_future.set_result(self._choice_options[idx].goto)
                event.stop()
