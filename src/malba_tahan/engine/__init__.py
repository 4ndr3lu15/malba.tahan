"""The visual-novel engine: story model, director, stage screen, and animated widgets.

The engine is deliberately content-agnostic. It knows how to *tell* a story —
reveal narration with a typewriter, cross-fade backgrounds, show a speaker's
dialogue, offer choices, and hand off to a bespoke puzzle screen — but it knows
nothing about any particular chapter. Chapters live as data in ``content/`` and
puzzles live as hand-crafted screens in ``puzzles/``.
"""
