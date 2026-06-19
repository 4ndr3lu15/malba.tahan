---
name: play
description: Launch the malba tahan visual novel (or the Textual dev console) to verify a change works in the real TUI. Use when asked to run, start, play, or screenshot the app.
---

# play malba tahan

This project is a Textual TUI visual novel. Use this to actually run it.

## launch the game

```bash
uv run malba.tahan
```

`uv` manages the environment; no activation needed. The app opens on an animated
title screen → "begin the journey" starts the prologue.

## dev console (for iterating on animations)

In one terminal:

```bash
uv run textual console
```

In another:

```bash
uv run textual run --dev malba_tahan.app:MalbaTahanApp
```

`print(...)` and Textual log output then show up in the console terminal.

## verify headlessly (no interactive terminal)

When you can't drive a live terminal, exercise the flow with Textual's pilot.
Pattern that works for this app:

```python
import asyncio
from malba_tahan.app import MalbaTahanApp

async def main():
    app = MalbaTahanApp()
    async with app.run_test(size=(100, 40)) as pilot:
        await pilot.pause(0.2)
        await pilot.click("#begin")          # start the story
        await pilot.press("space")           # advance a beat (skip-then-advance)
        # await pilot.press("1")             # pick choice option 1 when shown
        # app.screen.__class__.__name__      # inspect the current screen
        print(app.screen.__class__.__name__)

asyncio.run(main())
```

Notes:
- `space`/`enter` first fast-forwards the typewriter, then advances.
- A choice is open when `app.screen.query_one('#choices').display` is True;
  pick with number keys or `click('#choice-0')`.
- The balance puzzle needs at least one weigh before "identify" is enabled.
- `app.export_screenshot()` returns an SVG string for a visual snapshot.
