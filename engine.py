import numpy as np  # type: ignore
from typing import Iterable, Any

from tcod.context import Context
from tcod.console import Console
from tcod.map import compute_fov

import colors
from entity import Entity
from game_map import GameMap
from input_handlers import EventHandler

import time
import random

class Engine:
    TORCH_FLICKER_INTERVAL_MIN = 0.05
    TORCH_FLICKER_INTERVAL_MAX = 0.5
    TORCH_FLICKER_COLOR_MIN = -20
    TORCH_FLICKER_COLOR_MAX = 25

    def __init__(self, event_handler: EventHandler, game_map: GameMap, player: Entity):
        self.event_handler = event_handler
        self.game_map = game_map
        self.player = player
        self._last_flicker = time.time()
        self._next_flicker_interval = 1
        self.update_fov()

    def handle_enemy_turns(self) -> None:
        for entity in self.game_map.entities - {self.player}:
            print(f"The {entity.name} wonders when it will get to take a real turn")

    def handle_events(self, events: Iterable[Any]) -> None:
        for event in events:
            action = self.event_handler.dispatch(event)

            if action is None:
                continue

            action.perform(self, self.player)

            self.handle_enemy_turns()
            self.update_fov() # Update the FOV before the player's next action

    def update_fov(self) -> None:
        """Recompute the visible area based on the players point of view."""
        self.game_map.visible[:] = compute_fov(
            self.game_map.tiles["transparent"],
            (self.player.x, self.player.y),
            radius=self.player.light_radius
        )
        # If a tile is "visible" it should be added to "explored".
        self.game_map.explored |= self.game_map.visible

    def _flicker_torch(self):
        now = time.time()
        if now - self._last_flicker >= self._next_flicker_interval:
            base = np.array(colors.TORCH_BASE_RGB)
            variation = random.randint(self.TORCH_FLICKER_COLOR_MIN, self.TORCH_FLICKER_COLOR_MAX)
            color = np.clip(base + variation, 0, 255)
            flicker_color = tuple(color.astype(int))

            floor_mask = self.game_map.tiles["walkable"] & self.game_map.tiles["transparent"]
            self.game_map.tiles["light"]["bg"][floor_mask] = flicker_color
            self._next_flicker_interval = random.uniform(self.TORCH_FLICKER_INTERVAL_MIN, self.TORCH_FLICKER_INTERVAL_MAX)
            self._last_flicker = now

    def render(self, console: Console, context: Context) -> None:
        self._flicker_torch()

        self.game_map.render(console)

        context.present(console, keep_aspect=True, integer_scaling=True, clear_color=colors.MAP_BORDER_COLOR)

        console.clear()