from __future__ import annotations

from typing import TYPE_CHECKING

from constants import colors, general

if TYPE_CHECKING:
    from tcod import Console

def render_bar(
    console: Console, current_value: int, maximum_value: int, total_width: int
) -> None:
    bar_width = int(float(current_value) / maximum_value * total_width)

    console.draw_rect(x=1, y=general.HEIGHT_HP_BAR, width=total_width, height=1, ch=1, bg=colors.bar_empty)

    if bar_width > 0:
        console.draw_rect(x=1, y=general.HEIGHT_HP_BAR, width=bar_width, height=1, ch=1, bg=colors.bar_filled)

    console.print(x=2, y=general.HEIGHT_HP_BAR, string=f"<HP> {current_value:0>2}/{maximum_value:0>2}", fg=colors.bar_text)