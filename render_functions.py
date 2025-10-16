from __future__ import annotations

from collections import Counter
from typing import Optional, TYPE_CHECKING

from constants import colors, general

if TYPE_CHECKING:
    from tcod import Console, console
    from engine import Engine
    from game_map import GameMap


def get_names_at_location(x: int, y: int, game_map: GameMap) -> Optional[str]:
    if not game_map.in_bounds(x, y) or not game_map.visible[x, y]:
        return

    # For clarity do a few steps to get our entity names for viewing
    # We want to put the highest RenderOrder first in the list
    # Also put an (x2) or similar counter in the rare case of multiples on the same tile
    entities_here = [e for e in game_map.entities if e.x == x and e.y == y]
    if entities_here:
        entities_sorted = sorted(
            entities_here, key=lambda e: e.render_order.value, reverse=True
        )
        name_counts = Counter(e.name for e in entities_sorted)
        names = ", ".join(
            f"{name} (x{count})" if count > 1 else name
            for name, count in name_counts.items()
        )

        return names.capitalize()


def render_hp_bar(console: Console, current_value: int, maximum_value: int) -> None:
    # Draw the "full" background bar
    console.draw_rect(
        x=general.HP_BAR_X,
        y=general.HP_BAR_Y,
        width=general.HP_BAR_WIDTH,
        height=general.HP_BAR_HEIGHT,
        ch=1,
        bg=colors.bar_empty,
    )

    # Draw the current HP as a bar in front
    filled_bar_width = int(float(current_value) / maximum_value * general.HP_BAR_WIDTH)
    if filled_bar_width > 0:
        console.draw_rect(
            x=general.HP_BAR_X,
            y=general.HP_BAR_Y,
            width=filled_bar_width,
            height=general.HP_BAR_HEIGHT,
            ch=1,
            bg=colors.bar_filled,
        )

    # Draw the numeric HP text value
    console.print(
        x=general.HP_BAR_X + 1,
        y=general.HP_BAR_Y,
        string=f"<HP> {current_value:0>2}/{maximum_value:0>2}",  # Pad front zeroes
        fg=colors.bar_text,
    )


def render_names_at_mouse_location(
    console: Console, engine: Engine, x: int, y: int
) -> None:
    mouse_x, mouse_y = engine.mouse_location

    names_at_mouse_location = get_names_at_location(
        x=mouse_x, y=mouse_y, game_map=engine.game_map
    )

    if names_at_mouse_location:
        view_text = "VIEW?"
        console.print(x=x, y=y, string=view_text, bg=colors.view_bg)
        console.print(
            x=x + len(view_text) + 1,
            y=y,
            string=names_at_mouse_location,
            fg=colors.view_fg,
        )
