"""The application shell: an animated title screen that launches the story.

In 0.0.1 this module *was* the whole game. As of 0.0.2 the game is a visual
novel: this file is just the front door — a living title screen — and the actual
storytelling is done by the engine (:mod:`malba_tahan.engine`) playing chapters
from ``content/`` and handing off to bespoke puzzles in
:mod:`malba_tahan.puzzles`.
"""

from __future__ import annotations

from textual.app import App, ComposeResult
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Static

from .engine.novel_screen import NovelScreen
from .engine.story import StoryError, load_scene
from .engine.widgets import AmbientLayer
from .puzzles import make_puzzle, puzzle_ids

OPENING_CHAPTER = "00_prologue"

TITLE_ART = """\
╔════════════════════════════════════════════════╗
║   M  A  L  B  A      T  A  H  A  N              ║
║                                                 ║
║        ·  the man who counted  ·                ║
╚════════════════════════════════════════════════╝"""


class MenuScreen(Screen[None]):
    """The title screen: drifting desert stars behind a gold banner."""

    CSS = """
    MenuScreen { layers: sky ui; align: center middle; background: #0b1320; }
    #ambient { layer: sky; width: 100%; height: 100%; }
    #menu { layer: ui; width: auto; height: auto; align: center middle; }
    #logo {
        width: auto; content-align: center middle; color: #D4AF37;
        text-style: bold; padding: 0 0 1 0;
    }
    #tagline { width: 100%; text-align: center; color: #9ecbff; padding-bottom: 2; }
    #menu Button { width: 34; margin: 0 0 1 0; }
    """

    BINDINGS = [("q", "quit", "quit")]

    def compose(self) -> ComposeResult:
        yield AmbientLayer(id="ambient")
        with Vertical(id="menu"):
            yield Static(TITLE_ART, id="logo")
            yield Static("a terminal visual novel · inspired by malba tahan", id="tagline")
            yield Button("begin the journey", variant="success", id="begin")
            yield Button("continue (coming soon)", id="continue", disabled=True)
            yield Button("quit", id="quit")
        yield Footer()

    def on_mount(self) -> None:
        # gentle fade-in so the title arrives rather than just appearing.
        logo = self.query_one("#logo", Static)
        logo.styles.opacity = 0.0
        logo.styles.animate("opacity", value=1.0, duration=1.2)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        bid = event.button.id
        if bid == "begin":
            self._begin()
        elif bid == "quit":
            self.app.exit()

    def _begin(self) -> None:
        try:
            scene = load_scene(OPENING_CHAPTER, known_puzzles=puzzle_ids())
        except StoryError as exc:  # surface a malformed chapter instead of crashing
            self.notify(f"could not load chapter: {exc}", severity="error", timeout=8)
            return
        self.app.push_screen(NovelScreen(scene, make_puzzle))


class MalbaTahanApp(App[None]):
    """The man who counted — a terminal visual novel."""

    def on_mount(self) -> None:
        self.title = "malba tahan"
        self.sub_title = "the man who counted"
        self.push_screen(MenuScreen())


def run() -> None:
    MalbaTahanApp().run()
