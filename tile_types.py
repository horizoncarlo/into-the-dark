from typing import Tuple

from constants import colors, general
import numpy as np  # type: ignore

# Tile struct used for statically defined tile data.
tile_dt = np.dtype(
    [
        ("walkable", np.bool),  # True if this tile can be walked over.
        ("transparent", np.bool),  # True if this tile doesn't block FOV.
        ("dark", general.GRAPHIC_DT),  # Graphics for when this tile is not in FOV.
        ("light", general.GRAPHIC_DT),  # Graphics for when the tile is in FOV.
    ]
)


def new_tile(
    *,  # Enforce the use of keywords, so that parameter order doesn't matter.
    walkable: int,
    transparent: int,
    dark: Tuple[int, Tuple[int, int, int], Tuple[int, int, int]],
    light: Tuple[int, Tuple[int, int, int], Tuple[int, int, int]],
) -> np.ndarray:
    """Helper function for defining individual tile types"""
    return np.array((walkable, transparent, dark, light), dtype=tile_dt)


floor = new_tile(
    walkable=True,
    transparent=True,
    dark=(ord("░"), colors.FLOOR_FG_RGB, colors.FLOOR_BG_RGB),
    light=(ord("░"), colors.FLOOR_FG_RGB, colors.TORCH_BASE_RGB),
)

wall_color = dark = (ord("█"), colors.WALL_FG_RGB, colors.WALL_BG_RGB)
wall = new_tile(walkable=False, transparent=False, dark=wall_color, light=wall_color)
