import random
from typing import Tuple

import numpy as np  # type: ignore

from constants import colors, general

FLOOR_FG_RGB = (30, 30, 50)
FLOOR_BG_RGB = (20, 20, 20)
WALL_FG_RGB = (40, 40, 60)
WALL_BG_RGB = (80, 80, 80)

# Tile struct used for statically defined tile data
tile_dt = np.dtype(
    [
        ("walkable", np.bool),  # True if this tile can be walked over
        ("transparent", np.bool),  # True if this tile doesn't block FOV
        ("dark", general.GRAPHIC_DT),  # Graphics for when this tile is not in FOV
        ("light", general.GRAPHIC_DT),  # Graphics for when the tile is in FOV
    ]
)


def new_tile(
    *,  # Enforce the use of keywords, so that parameter order doesn't matter
    walkable: int,
    transparent: bool = False,
    dark: Tuple[int, Tuple[int, int, int], Tuple[int, int, int]],
    light: Tuple[int, Tuple[int, int, int], Tuple[int, int, int]],
) -> np.ndarray:
    """Helper function for defining individual tile types"""
    return np.array((walkable, transparent, dark, light), dtype=tile_dt)


down_stairs = new_tile(
    walkable=True,
    dark=(ord(">"), (0, 0, 100), (50, 50, 150)),
    light=(ord(">"), (170, 170, 190), (105, 105, 105)),
)


def make_floor(
    light_char="░", dark_char="░", dark_fg=FLOOR_FG_RGB, dark_bg=FLOOR_BG_RGB
):
    return new_tile(
        walkable=True,
        transparent=True,
        dark=(ord(dark_char), dark_fg, dark_bg),
        light=(
            ord(light_char),
            colors.TORCH_FG_BASE,
            colors.TORCH_BG_BASE,
        ),  # Can't customize light_bg as the torch relies on it
    )


def make_wall(
    light_char="█",
    light_fg=WALL_FG_RGB,
    light_bg=WALL_BG_RGB,
    dark_char="█",
    dark_fg=WALL_FG_RGB,
    dark_bg=WALL_BG_RGB,
):
    return new_tile(
        walkable=False,
        transparent=False,
        dark=(ord(dark_char), dark_fg, dark_bg),
        light=(ord(light_char), light_fg, light_bg),
    )


# Top level variables that other places reference...how vague
floor = make_floor()
wall = make_wall()


def generate_tiles():
    global floor, wall

    floor_char = random.choice([" ", "░", "▒", "▓", "■", ".", "_", "-", "=", "○", "•"])
    floor_dark_bg = random.randint(20, 60)  # Varying shades of gray
    floor_dark_fg = random.randint(50, 90)
    floor = make_floor(
        light_char=floor_char,
        dark_char=floor_char,
        dark_fg=floor_dark_fg,
        dark_bg=floor_dark_bg,
    )

    wall_char = random.choice([" ", "░", "▒", "▓", "█", "■", "♣", "♠", "#"])
    # Generate a base color for the walls, with a potential modifier for rgb, then skew the bg based on that
    wall_color_base = random.randint(20, 100)
    wall_color_multi = [
        random.randint(0, 2),
        random.randint(0, 2),
        random.randint(0, 2),
    ]
    wall_color_fg = (
        min(wall_color_base * wall_color_multi[0], 255),
        min(wall_color_base * wall_color_multi[1], 255),
        min(wall_color_base * wall_color_multi[2], 255),
    )
    wall_color_mod = random.randint(0, 100)
    wall_color_bg = tuple(max(c - wall_color_mod, 0) for c in wall_color_fg)

    wall = make_wall(
        light_char=wall_char,
        light_fg=wall_color_fg,
        light_bg=wall_color_bg,
        dark_char=wall_char,
        dark_fg=wall_color_fg,
        dark_bg=wall_color_bg,
    )
