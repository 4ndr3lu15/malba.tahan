---
name: new-chapter
description: Scaffold a new story chapter (a Scene YAML) for the malba tahan visual novel. Use when adding a chapter of the book or a new narrative scene.
---

# new chapter

A chapter is **data**: one YAML scene under
`src/malba_tahan/content/chapters/`. No engine code is needed unless the chapter
introduces a brand-new puzzle (then also run `/new-puzzle`).

## steps

1. Pick the next number and a slug, e.g. `01_the_thirty_five_camels.yaml`.
   Chapters are loaded by name (without `.yaml`) via `story.load_scene(...)`.
2. Create the file from the template below.
3. Add any new speakers to `src/malba_tahan/content/characters.yaml`.
4. Add any background art as `src/malba_tahan/assets/art/<name>.txt` (plain
   text; gold colour is applied by the stage).
5. If the chapter should be reachable from the menu, wire it up in `app.py`
   (currently `OPENING_CHAPTER = "00_prologue"`); continue/chapter-select is a
   0.0.3 concern.
6. Verify it loads and validates:
   ```bash
   uv run python -c "from malba_tahan.engine.story import load_scene; from malba_tahan.puzzles import puzzle_ids; print(load_scene('01_the_thirty_five_camels', known_puzzles=puzzle_ids()).title)"
   ```
   then play it with `/play`.

## template

```yaml
id: <slug>
title: "<chapter title shown in the header>"

beats:
  - art: <background-name>            # optional opening background

  - narration: "set the scene in the narrator's voice."
  - say: <character-id>
    text: "a line of dialogue."

  - choice: "what do you do?"
    options:
      - text: "first option"
        goto: path_a
      - text: "second option"
        goto: path_b

  - label: path_a
  - narration: "..."
  - goto: trial

  - label: path_b
  - narration: "..."

  - label: trial
  - puzzle: <puzzle-id>              # must exist in puzzles/__init__.py REGISTRY
    on_win: won
    on_lose: lost

  - label: won
  - narration: "the reward / the story moves forward."
  - goto: finish

  - label: lost
  - narration: "a gentler turn; the story still continues."

  - label: finish
  - end: "— closing line —"
```

## beat reference

- `narration:` / `say:`+`text:` — text beats; optional `art:` and `speed:` (cps).
- `choice:`+`options:` (`text`,`goto`) — branch to a `label`.
- `puzzle:`+`on_win`/`on_lose` — hand off to a registered puzzle, branch on result.
- `art:` (+`transition: fade|cut`), `label:`, `goto:`, `end:`.

The loader validates labels and puzzle ids at load time and raises `StoryError`
on anything dangling — fix those before shipping the chapter.

## house style

Lowercase user-facing prose. Keep the desert/arabian-nights tone of the source
book. The player is Beremiz; the narrator is "the traveller".
