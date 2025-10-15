from __future__ import annotations
import numpy as np  # type: ignore

from typing import TYPE_CHECKING, Tuple

import tcod.constants
from tcod.context import Context
from tcod.console import Console
from tcod.map import compute_fov

from constants import colors, general
from input_handlers import MainGameEventHandler

import time
import random

if TYPE_CHECKING:
    from entity import Actor
    from game_map import GameMap
    from input_handlers import EventHandler

class Engine:
    game_map: GameMap

    def __init__(self, player: Actor):
        self.event_handler: EventHandler = MainGameEventHandler(self)
        self.player = player
        self._last_flicker = time.time()
        self._next_flicker_interval = 1

    def handle_enemy_turns(self) -> None:
        for entity in self.game_map.entities - {self.player}:
            if entity.ai:
                entity.ai.perform()

    def update_fov(self) -> None:
        """Recompute the visible area based on the players point of view"""
        self.game_map.visible[:] = compute_fov(
            self.game_map.tiles["transparent"],
            (self.player.x, self.player.y),
            radius=self.player.light_radius,
            # TODO See the really good article on the FOV options:
            # https://www.roguebasin.com/index.php?title=Comparative_study_of_field_of_view_algorithms_for_2D_grid_based_worlds
            algorithm=tcod.constants.FOV_PERMISSIVE_1
        )
        # If a tile is "visible" it should be added to "explored".
        self.game_map.explored |= self.game_map.visible

    def _flicker_torch(self):
        now = time.time()
        if now - self._last_flicker >= self._next_flicker_interval:
            base = np.array(colors.TORCH_BASE_RGB)
            variation = random.randint(general.TORCH_FLICKER_COLOR_MIN, general.TORCH_FLICKER_COLOR_MAX)
            color = np.clip(base + variation, 0, 255)
            self._last_flicker = now
            self._next_flicker_interval = random.uniform(general.TORCH_FLICKER_INTERVAL_MIN,
                                                         general.TORCH_FLICKER_INTERVAL_MAX)

            self._update_floor_color(tuple(color.astype(int)))

    def _update_floor_color(self, color: Tuple[int, int, int]) -> None:
        floor_mask = self.game_map.tiles["walkable"] & self.game_map.tiles["transparent"]
        self.game_map.tiles["light"]["bg"][floor_mask] = color

    def render(self, console: Console, context: Context) -> None:
        if self.player.is_alive:
            self._flicker_torch()
        else:
            self._update_floor_color((0, 0, 0))

        console.print(
            x=1,
            y=general.HEIGHT - 2, # Bit of padding near the bottom
            string=f"HP: {self.player.fighter.hp}/{self.player.fighter.max_hp}",
        )

        self.game_map.render(console)

        context.present(console, keep_aspect=True, integer_scaling=True, clear_color=colors.MAP_BORDER_COLOR)

        console.clear()