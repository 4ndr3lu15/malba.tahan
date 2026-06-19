# malba tahan — 8 weights of gold

a terminal toy inspired by the spirit of the brazilian book **"the man who
counted"** (*o homem que calculava*) by **malba tahan**, which also gives this
repository its name.

you are challenged with a classic balance puzzle: among **8 gold balls**, one is
slightly **heavier** than the rest. discover which one using the balance scale at
most **twice**.

this is a full rewrite of the original web demo as a **beautiful terminal
application**, written in **python** with the [textual](https://textual.textualize.io/)
tui framework and managed with [**uv**](https://docs.astral.sh/uv/).

---

## overview

- **goal**: find the single heaviest ball among eight that look identical.
- **constraint**: you may use the **weigh** action at most **twice**.
- **outcome**:
  - identify the heavy ball correctly → you win the sultan's favour.
  - guess wrong (or run out of weighings and miss) → you lose the challenge.

the heavy ball is chosen at random at the start of each round and is **not**
visibly different — only the scale can reveal it. the game simulates the balance
and counts your weighings; finding the answer in two weighings is up to you, like
a true *man who counted*.

---

## running it

you only need [uv](https://docs.astral.sh/uv/) installed; it manages python and
all dependencies for you.

```bash
# from the project directory
uv run malba.tahan
```

that's it — `uv` creates the environment, installs textual, and launches the app.

alternatively:

```bash
uv run python -m malba_tahan
```

---

## how to play

the screen shows a balance scale, a status line (weighings used, balls per pan),
control buttons, and the eight gold balls in a staging area below.

everything works with **mouse clicks** or **keyboard shortcuts**.

1. **select a ball** — click a ball in the staging area (it highlights).
2. **place it on a pan** — click **◀ place on left** or **place on right ▶**
   (or press `l` / `r`).
3. **return a ball** — click a ball that is already on a pan to send it back to
   staging. **clear pans** (`c`) empties both pans at once.
4. **weigh** — the **weigh** button (`w`) enables only when **both pans hold the
   same number of balls** (at least one each). the beam tips toward the heavier
   side; the heavier pan visibly sinks.
5. **identify** — after your second weighing the game switches to identify mode
   automatically. you can also enter it earlier with **identify heavy ball**
   (`i`). in identify mode, click the ball you believe is heaviest.
6. **result** — a win/lose overlay appears. choose **play again** to start a
   fresh round (or press `n` at any time for a new game).

### keyboard shortcuts

| key | action |
| --- | --- |
| `w` | weigh |
| `l` | place selected ball on the left pan |
| `r` | place selected ball on the right pan |
| `c` | clear both pans |
| `i` | toggle identify mode |
| `n` | new game |
| `q` | quit |

---

## project layout

```
src/malba_tahan/
├── game.py        # pure puzzle logic (no ui) — rules, weighing, guessing
├── scale_art.py   # renders the balance scale as terminal art (tilts with weight)
├── app.py         # the textual ui: layout, styling, interaction
└── __main__.py    # console entry point
tests/
└── test_game.py   # unit tests for the game logic
```

- **`game.py`** holds the rules with no ui dependency, so the mechanic is easy to
  test: eight balls, one heavier, at most two weighings, win/lose on guess.
- **`scale_art.py`** draws the beam, chains and pans onto a character grid so the
  figure always lines up; the heavier pan dips downward.
- **`app.py`** is a thin view layer over the game, in the original night-desert
  gold colour scheme.

---

## development

```bash
# install dev dependencies (pytest, textual-dev)
uv sync --extra dev

# run the tests
uv run pytest

# run the textual debug console (in a second terminal) while developing
uv run textual run --dev malba_tahan.app:MalbaTahanApp
```

---

## notes and limitations

- the mechanic (two weighings, one heavier ball among eight) follows the classic
  balance puzzle often associated with mathematical riddles like those of
  **malba tahan**.
- there is no "reveal answer" option: the heavy ball's identity is only exposed
  by the game's own logic when it checks your guess.
- the game does **not** enforce an optimal strategy — it simply simulates the
  balance, counts the weighings, and reports the result.
