# malba tahan — the man who counted

a terminal **visual novel** inspired by the brazilian book **"the man who
counted"** (*o homem que calculava*) by **malba tahan**, which also gives this
repository its name.

the story is narrated, and as it unfolds you stand in the sandals of **beremiz
samir**, the man who counted. when beremiz meets a riddle, so do you — and solving
the puzzle carries the story forward.

written in **python** with the [textual](https://textual.textualize.io/) tui
framework and managed with [**uv**](https://docs.astral.sh/uv/).

---

## status (v0.0.2)

an early **prototype of the visual-novel system**:

- an animated title screen and a narrated **prologue** — meeting beremiz on the
  road to baghdad,
- a typewriter dialogue box, cross-fading ascii backgrounds, branching choices,
- and the first bespoke puzzle, the **trial of the eight gold balls** (find the
  one heavier ball with a balance, in two weighings), woven into the story so the
  outcome changes what beremiz says next.

the roadmap:

- **0.0.x** — build and polish the engine and the way puzzles plug into it.
- **0.1.0+** — add the book itself, one chapter at a time.

---

## running it

you only need [uv](https://docs.astral.sh/uv/); it manages python and all
dependencies for you.

```bash
uv run malba.tahan
```

advance dialogue with **space** / **enter** (press once to reveal the whole line,
again to continue); pick choices with the number keys or by clicking.

---

## project layout

```
src/malba_tahan/
├── app.py            # animated title/menu shell → launches the story
├── engine/           # the visual-novel engine (content-agnostic)
│   ├── anim.py       # pure animation math (typewriter, easing) — unit-tested
│   ├── widgets.py    # animated widgets (typewriter, ascii art, name plate, ambient stars)
│   ├── story.py      # scene/beat model + yaml loader + validation
│   ├── assets.py     # loads ascii art
│   ├── director.py   # walks the beats, branches on puzzle results
│   └── novel_screen.py  # the stage (background + dialogue box)
├── puzzles/          # bespoke, hand-crafted puzzle screens (balance, ...)
├── game.py           # pure balance-puzzle rules (no ui) — unit-tested
├── scale_art.py      # renders the balance scale
├── content/          # the story as data: characters.yaml + chapters/*.yaml
└── assets/art/       # hand-drawn ascii/unicode backgrounds
tests/                # unit tests for the pure logic
```

see [`CLAUDE.md`](CLAUDE.md) for the architecture, the chapter/beat schema, and
how to author new chapters and puzzles.

---

## development

```bash
uv sync --extra dev    # install dev deps (pytest, textual-dev)
uv run pytest          # run the tests
uv run textual run --dev malba_tahan.app:MalbaTahanApp   # dev console
```
