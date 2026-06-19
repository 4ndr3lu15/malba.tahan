# malba tahan — project guide for claude

A terminal **visual novel** inspired by Malba Tahan's *O Homem que Calculava*
("The Man Who Counted"). The story is narrated; as it unfolds the player stands
in for **Beremiz Samir**, the man who counted, and solves the puzzles he faces.
Solving a puzzle advances the story.

Built with **Textual** (the TUI framework) and managed with **uv**.

## roadmap / versioning

- **0.0.x** — the engine. Prototype and then polish the visual-novel system and
  the way bespoke puzzles plug into it. (0.0.2 = first working prototype: an
  animated title, the prologue chapter, and the balance puzzle wired in.)
- **0.1.0+** — the book. Add one chapter at a time, re-read by re-read, as YAML
  story scripts plus hand-crafted puzzles.

When asked to "add a chapter", that's data + a puzzle, not new engine code.

## architecture

```
src/malba_tahan/
├── app.py            # shell: animated title/menu screen → launches the director
├── engine/           # the visual-novel engine (content-agnostic)
│   ├── anim.py       # PURE animation math (typewriter, frame cycler, easing) — unit-tested
│   ├── widgets.py    # animated widgets: TypewriterText, AsciiArtPanel, NamePlate, AmbientLayer
│   ├── story.py      # Scene/Beat dataclasses + YAML loader + validation + flow helpers
│   ├── assets.py     # loads ascii art from assets/art/*.txt
│   ├── director.py   # async worker: walks beats, awaits input/puzzle results, branches
│   └── novel_screen.py  # the stage: background panel + dialogue box; director's view
├── puzzles/          # bespoke, hand-crafted puzzle screens
│   ├── __init__.py   # REGISTRY: puzzle id -> screen factory
│   └── balance.py    # the 8-balls balance puzzle
├── game.py           # PURE balance-puzzle rules (no UI) — unit-tested
├── scale_art.py      # renders the balance scale as terminal art
├── content/
│   ├── characters.yaml      # the cast (name, colour per speaker)
│   └── chapters/NN_*.yaml   # one scene per chapter
└── assets/art/*.txt  # hand-drawn ascii/unicode backgrounds
```

### how a chapter plays (the flow)

`MenuScreen` (app.py) loads a chapter via `story.load_scene(...)` and pushes a
`NovelScreen`. On mount the screen starts the `Director` as a Textual worker. The
director walks the scene's beats and calls the screen's small async vocabulary:
`set_art`, `show_text`, `ask_choice`, `run_puzzle`, `show_end`. For a `puzzle`
beat it does `await push_screen_wait(make_puzzle(id))`, gets a `PuzzleResult`,
and branches on `result.won`.

### the scene / beat schema (content/chapters/*.yaml)

Top level: `id`, `title`, and a list of `beats`. Each beat is a one-key mapping
naming its kind:

- `narration: "..."` — narrator voice. Optional `art: <name>`, `speed: <cps>`.
- `say: <character-id>` + `text: "..."` — dialogue. Optional `art`, `speed`.
- `choice: "prompt"` + `options: [{text, goto}]` — branch to a `label`.
- `puzzle: <id>` + optional `on_win: <label>` / `on_lose: <label>`.
- `art: <name>` (+ optional `transition: fade|cut`) — change background only.
- `label: <name>` — a jump target. `goto: <label>` — jump to one.
- `end: "closing line"` — end the scene.

The loader validates every `goto`/choice/branch label resolves and every
`puzzle` id is in the registry; a bad chapter raises `StoryError` instead of
crashing a play session. Characters referenced by `say` should exist in
`content/characters.yaml`.

## conventions

- **User-facing prose is lowercase** (intentional house style — see existing
  copy). Keep it.
- **Palette**: gold `#D4AF37` is the signature colour; dark navy `#0b1320`
  background, `#101c30` panels. Reuse these.
- **Keep animation math in `engine/anim.py`** (pure, testable); widgets apply it
  to Textual timers/`styles.animate`. Don't bury timing logic inside widgets.
- **Puzzles are artisanal**, not instances of a generic base. The only contract:
  a puzzle is a `Screen` that `dismiss(...)`es with a `PuzzleResult(won=...)`.
  Register it in `puzzles/__init__.py` and reference its id from a chapter.
- **Pure logic stays UI-free** (`game.py`, `engine/story.py`, `engine/anim.py`)
  so it can be unit-tested without a running app.

## running & testing

```bash
uv sync --extra dev            # install deps (textual, pyyaml, pytest, textual-dev)
uv run malba.tahan             # play it
uv run pytest                  # run the unit tests
uv run textual run --dev malba_tahan.app:MalbaTahanApp   # dev console for animations
```

For verifying UI changes without a terminal, drive the app headlessly with
Textual's `App.run_test()` pilot (see how the flow is exercised — click `#begin`,
`press('space')` to advance, `press('1')` for choices).

## skills

- `/play` — launch the app (or the dev console) to verify a change.
- `/new-chapter` — scaffold a new `content/chapters/NN_*.yaml`.
- `/new-puzzle` — scaffold a new bespoke puzzle module + registry entry.
