"""Renders the balance scale as terminal art.

The art is drawn onto a fixed character grid so the beam, chains and pans always
line up. The whole figure is returned as a Rich-markup string; the heavier pan
visibly tips downward.
"""

from __future__ import annotations

from .game import Tilt

GRID_W = 45
GRID_H = 13

PAN_INNER = 11
PAN_LEFT_X = 4
PAN_RIGHT_X = 26
PIVOT_X = 22

BEAM_BASE_Y = 2
BEAM_DROP = 1
CHAIN_LEN = 2


def _blank_grid() -> list[list[str]]:
    return [[" "] * GRID_W for _ in range(GRID_H)]


def _stamp(grid: list[list[str]], x: int, y: int, text: str) -> None:
    if y < 0 or y >= GRID_H:
        return
    for i, ch in enumerate(text):
        col = x + i
        if 0 <= col < GRID_W:
            grid[y][col] = ch


def _draw_arm(grid: list[list[str]], x_end: int, y_end: int, x_pivot: int, y_pivot: int) -> None:
    """Draw a beam arm from a pan end to the pivot, sloping if tilted."""
    step = 1 if x_pivot >= x_end else -1
    cols = list(range(x_end, x_pivot + step, step))
    span = max(len(cols) - 1, 1)
    for i, col in enumerate(cols):
        if col == x_pivot:
            continue
        y = round(y_end + (y_pivot - y_end) * i / span)
        y_next = round(y_end + (y_pivot - y_end) * (i + 1) / span)
        if y_next < y:
            ch = "╱" if step > 0 else "╲"
        elif y_next > y:
            ch = "╲" if step > 0 else "╱"
        else:
            ch = "═"
        _stamp(grid, col, y, ch)


def _pan_box(label: str, ids: list[int]) -> list[str]:
    contents = " ".join(str(b + 1) for b in sorted(ids)) if ids else "·"
    return [
        "╭" + "─" * PAN_INNER + "╮",
        "│" + label.center(PAN_INNER) + "│",
        "│" + contents.center(PAN_INNER) + "│",
        "╰" + "─" * PAN_INNER + "╯",
    ]


def render_scale(left_ids: list[int], right_ids: list[int], tilt: Tilt | None) -> str:
    """Return Rich-markup art of the scale for the given pan contents and tilt."""
    grid = _blank_grid()

    if tilt is Tilt.LEFT:
        left_y, right_y = BEAM_BASE_Y + BEAM_DROP, BEAM_BASE_Y - BEAM_DROP
    elif tilt is Tilt.RIGHT:
        left_y, right_y = BEAM_BASE_Y - BEAM_DROP, BEAM_BASE_Y + BEAM_DROP
    else:
        left_y = right_y = BEAM_BASE_Y

    left_center = PAN_LEFT_X + 1 + PAN_INNER // 2
    right_center = PAN_RIGHT_X + 1 + PAN_INNER // 2

    # Pivot mast + top ring (always fixed).
    _stamp(grid, PIVOT_X - 1, 0, "▟█▙")
    _stamp(grid, PIVOT_X, 1, "┃")

    # Beam arms slope from each pan end up to the fixed pivot.
    _draw_arm(grid, left_center, left_y, PIVOT_X, BEAM_BASE_Y)
    _draw_arm(grid, right_center, right_y, PIVOT_X, BEAM_BASE_Y)
    _stamp(grid, PIVOT_X, BEAM_BASE_Y, "╪")

    # Chains hang from each beam end down to the pan top.
    for k in range(1, CHAIN_LEN + 1):
        _stamp(grid, left_center, left_y + k, "│")
        _stamp(grid, right_center, right_y + k, "│")

    # Pan boxes.
    left_box = _pan_box("left", left_ids)
    right_box = _pan_box("right", right_ids)
    left_top = left_y + CHAIN_LEN + 1
    right_top = right_y + CHAIN_LEN + 1
    for i, line in enumerate(left_box):
        _stamp(grid, PAN_LEFT_X, left_top + i, line)
    for i, line in enumerate(right_box):
        _stamp(grid, PAN_RIGHT_X, right_top + i, line)

    # Stand / base under the pivot.
    _stamp(grid, PIVOT_X - 4, GRID_H - 2, "╲▁▁▁┃▁▁▁╱")
    _stamp(grid, PIVOT_X - 6, GRID_H - 1, "▔▔▔▔▔▔▔▔▔▔▔▔▔")

    rows = ["".join(row).rstrip() for row in grid]
    body = "\n".join(rows)
    return f"[#D4AF37]{body}[/]"
