"""The balance puzzle — the first bespoke puzzle.

Eight gold balls look identical; one is slightly heavier. Find it with the
balance scale in at most two weighings. The pure rules live in
:mod:`malba_tahan.game` (unchanged from 0.0.1) and the scale art in
:mod:`malba_tahan.scale_art`; this screen is the interactive shell around them,
restyled for the visual novel and returning a
:class:`~malba_tahan.engine.director.PuzzleResult` to the story.
"""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Center, Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Footer, Static

from ..engine.director import PuzzleResult
from ..game import Game, GameError, Location, Tilt
from ..scale_art import render_scale

GOLD = "#D4AF37"


class _ResultOverlay(ModalScreen[None]):
    """Brief win/lose flourish shown over the puzzle before it hands back."""

    CSS = """
    _ResultOverlay { align: center middle; }
    #result-box {
        width: 60;
        height: auto;
        padding: 2 4;
        border: thick #D4AF37;
        background: #101c30;
        align: center middle;
    }
    #result-box.lost { border: thick #8B0000; }
    #result-title {
        width: 100%;
        text-align: center;
        text-style: bold;
        color: #D4AF37;
        padding-bottom: 1;
    }
    #result-box.lost #result-title { color: #e57373; }
    #result-message { width: 100%; text-align: center; padding-bottom: 1; }
    #result-box Button { width: 100%; }
    """

    def __init__(self, won: bool, message: str) -> None:
        super().__init__()
        self._won = won
        self._message = message

    def compose(self) -> ComposeResult:
        title = "✦ the sultan is pleased ✦" if self._won else "✦ the sultan frowns ✦"
        with Vertical(id="result-box", classes="won" if self._won else "lost"):
            yield Static(title, id="result-title")
            yield Static(self._message, id="result-message")
            yield Button("continue ▸", variant="success", id="continue")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(None)


class BalancePuzzleScreen(ModalScreen[PuzzleResult]):
    """The interactive balance puzzle; dismisses with a PuzzleResult."""

    CSS = """
    BalancePuzzleScreen { background: #0b1320; color: #E0E0E0; align: center top; }
    #title {
        width: 100%; text-align: center; text-style: bold; color: #D4AF37; padding: 1 0 0 0;
    }
    #subtitle { width: 100%; text-align: center; color: #A0A0A0; }
    #status { width: 100%; text-align: center; padding: 1 0; color: #F3E5AB; }
    #scale { width: 100%; content-align: center middle; height: 14; }
    .panel-label { width: 100%; text-align: center; color: #A0A0A0; text-style: italic; }
    #controls, #placement, #staging {
        width: 100%; height: auto; align: center middle; padding: 0 0 1 0;
    }
    Button { margin: 0 1; }
    .ball { min-width: 7; }
    .ball.selected { background: #F3E5AB; color: #0b1320; text-style: bold; }
    .ball.on-left, .ball.on-right { background: #3E2723; color: #D4AF37; }
    """

    BINDINGS = [
        ("w", "weigh", "weigh"),
        ("l", "place_left", "→ left pan"),
        ("r", "place_right", "→ right pan"),
        ("c", "clear_pans", "clear pans"),
        ("i", "identify", "identify"),
        ("n", "new_game", "new round"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.game = Game()
        self.selected: int | None = None
        self.identify_mode = False

    # -- layout -------------------------------------------------------------
    def compose(self) -> ComposeResult:
        yield Static("the trial of the eight gold balls", id="title")
        yield Static(
            "one of the eight gold balls is slightly heavier. "
            "find it using the balance at most twice.",
            id="subtitle",
        )
        yield Static("", id="status")
        yield Static("", id="scale")
        with Horizontal(id="controls"):
            yield Button("weigh", variant="success", id="weigh")
            yield Button("identify heavy ball", variant="warning", id="identify")
            yield Button("clear pans", id="clear")
            yield Button("new round", id="new")
        with Horizontal(id="placement"):
            yield Button("◀ place on left", variant="primary", id="place-left")
            yield Button("place on right ▶", variant="primary", id="place-right")
        yield Static("— the eight gold balls —", classes="panel-label")
        with Center():
            with Horizontal(id="staging"):
                for i in range(self.game.total_balls):
                    yield Button(str(i + 1), id=f"ball-{i}", classes="ball")
        yield Footer()

    def on_mount(self) -> None:
        self.refresh_view("select a ball, then place it on a pan.")

    # -- rendering ----------------------------------------------------------
    def refresh_view(self, message: str) -> None:
        g = self.game
        self.query_one("#scale", Static).update(
            render_scale(g.balls_in(Location.LEFT), g.balls_in(Location.RIGHT), g.last_tilt)
        )

        left, right = g.pan_counts()
        status = (
            f"[{GOLD}]weighings:[/] {g.weighings_taken} / {g.max_weighings}    "
            f"[{GOLD}]left:[/] {left}    [{GOLD}]right:[/] {right}\n{message}"
        )
        self.query_one("#status", Static).update(status)

        for i in range(g.total_balls):
            button = self.query_one(f"#ball-{i}", Button)
            loc = g.locations[i]
            button.set_class(self.selected == i and not self.identify_mode, "selected")
            button.set_class(loc == Location.LEFT, "on-left")
            button.set_class(loc == Location.RIGHT, "on-right")

        self.query_one("#weigh", Button).disabled = not g.can_weigh() or self.identify_mode
        identify_btn = self.query_one("#identify", Button)
        identify_btn.disabled = g.weighings_taken == 0
        identify_btn.label = "cancel identify" if self.identify_mode else "identify heavy ball"
        for bid in ("place-left", "place-right", "clear"):
            self.query_one(f"#{bid}", Button).disabled = self.identify_mode

    # -- actions ------------------------------------------------------------
    def action_weigh(self) -> None:
        try:
            tilt = self.game.weigh()
        except GameError as exc:
            self.refresh_view(f"[#e57373]{str(exc).lower()}[/]")
            return
        self.selected = None
        verdict = {
            Tilt.LEFT: "the left pan sinks — it is heavier.",
            Tilt.RIGHT: "the right pan sinks — it is heavier.",
            Tilt.LEVEL: "the pans balance perfectly.",
        }[tilt]
        if self.game.weighings_left == 0:
            self._enter_identify(f"{verdict}  no weighings left — choose the heavy ball!")
        else:
            self.refresh_view(f"{verdict}  ({self.game.weighings_left} weighing left)")

    def action_place_left(self) -> None:
        self._place(Location.LEFT)

    def action_place_right(self) -> None:
        self._place(Location.RIGHT)

    def _place(self, pan: Location) -> None:
        if self.identify_mode:
            return
        if self.selected is None:
            self.refresh_view("select a ball from the staging area first.")
            return
        if self.game.locations[self.selected] != Location.STAGING:
            self.refresh_view("that ball is already on a pan. click it to return it first.")
            return
        ball = self.selected
        self.game.place(ball, pan)
        self.selected = None
        self.refresh_view(f"ball {ball + 1} placed on the {pan.value} pan.")

    def action_clear_pans(self) -> None:
        if self.identify_mode:
            return
        self.game.clear_pans()
        self.selected = None
        self.refresh_view("all balls returned to the staging area.")

    def action_identify(self) -> None:
        if self.game.weighings_taken == 0:
            self.refresh_view("weigh at least once before identifying.")
            return
        if self.identify_mode:
            self.identify_mode = False
            self.refresh_view("identify cancelled. keep playing.")
        else:
            self._enter_identify("click the ball you believe is the heaviest.")

    def _enter_identify(self, message: str) -> None:
        self.identify_mode = True
        self.selected = None
        self.refresh_view(message)

    def action_new_game(self) -> None:
        self.game.new_game()
        self.selected = None
        self.identify_mode = False
        self.refresh_view("new round! select a ball, then place it on a pan.")

    # -- events -------------------------------------------------------------
    def on_button_pressed(self, event: Button.Pressed) -> None:
        bid = event.button.id or ""
        if bid == "weigh":
            self.action_weigh()
        elif bid == "identify":
            self.action_identify()
        elif bid == "clear":
            self.action_clear_pans()
        elif bid == "new":
            self.action_new_game()
        elif bid == "place-left":
            self.action_place_left()
        elif bid == "place-right":
            self.action_place_right()
        elif bid.startswith("ball-"):
            self._on_ball(int(bid.removeprefix("ball-")))

    def _on_ball(self, ball: int) -> None:
        if self.identify_mode:
            self._make_guess(ball)
            return
        loc = self.game.locations[ball]
        if loc != Location.STAGING:
            self.game.place(ball, Location.STAGING)
            self.selected = None
            self.refresh_view(f"ball {ball + 1} returned to staging.")
        elif self.selected == ball:
            self.selected = None
            self.refresh_view("selection cleared.")
        else:
            self.selected = ball
            self.refresh_view(
                f"ball {ball + 1} selected. place it on a pan, or press it again to deselect."
            )

    def _make_guess(self, ball: int) -> None:
        won = self.game.guess(ball)
        if won:
            message = f"ball {ball + 1} truly was the heaviest. you have the eye of a sage!"
        else:
            heavy = self.game.heavy_ball + 1
            message = f"ball {ball + 1} was not the heaviest — it was ball {heavy}."
        self.identify_mode = False
        self.refresh_view(message)
        result = PuzzleResult(won=won, detail=message)

        def _hand_back(_: None) -> None:
            # statement form: don't *return* the dismiss awaitable, or Textual
            # would try to await it from within this callback and complain.
            self.dismiss(result)

        self.app.push_screen(_ResultOverlay(won, message), _hand_back)
