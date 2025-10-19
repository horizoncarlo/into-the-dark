from __future__ import annotations
import numpy as np  # type: ignore

from typing import TYPE_CHECKING, Tuple

import tcod.constants
from tcod.context import Context
from tcod.console import Console
from tcod.map import compute_fov

import exceptions
from constants import colors, general
from input_handlers import MainGameEventHandler
from message_log import MessageLog

import time
import random

from render_functions import render_hp_bar, render_names_at_mouse_location

if TYPE_CHECKING:
    from entity import Actor
    from game_map import GameMap
    from input_handlers import EventHandler


class Engine:
    game_map: GameMap

    def __init__(self, player: Actor):
        self.event_handler: EventHandler = MainGameEventHandler(self)
        self.message_log: MessageLog = MessageLog()
        self.mouse_location = (0, 0)
        self.player = player
        self._last_flicker = time.time()
        self._next_flicker_interval = 1

    def handle_enemy_turns(self) -> None:
        for entity in self.game_map.entities - {self.player}:
            try:
                getattr(entity, "ai", None) and entity.ai.perform()
            except exceptions.ImpossibleAction:
                pass  # AI can get away with annnnything these days! So ignore it

    def update_fov(self) -> None:
        """Recompute the visible area based on the players point of view"""
        self.game_map.visible[:] = compute_fov(
            self.game_map.tiles["transparent"],
            (self.player.x, self.player.y),
            radius=self.player.light_radius,
            # TODO See the really good article on the FOV options:
            # https://www.roguebasin.com/index.php?title=Comparative_study_of_field_of_view_algorithms_for_2D_grid_based_worlds
            algorithm=tcod.constants.FOV_PERMISSIVE_1,
        )
        # If a tile is "visible" it should be added to "explored".
        self.game_map.explored |= self.game_map.visible

    def _flicker_torch(self):
        now = time.time()
        if now - self._last_flicker >= self._next_flicker_interval:
            base = np.array(colors.TORCH_BASE_RGB)
            variation = random.randint(
                general.TORCH_FLICKER_COLOR_MIN, general.TORCH_FLICKER_COLOR_MAX
            )
            color = np.clip(base + variation, 0, 255)
            self._last_flicker = now
            self._next_flicker_interval = random.uniform(
                general.TORCH_FLICKER_INTERVAL_MIN, general.TORCH_FLICKER_INTERVAL_MAX
            )

            self._update_floor_color(tuple(color.astype(int)))

    def _update_floor_color(self, color: Tuple[int, int, int]) -> None:
        floor_mask = (
            self.game_map.tiles["walkable"] & self.game_map.tiles["transparent"]
        )
        self.game_map.tiles["light"]["bg"][floor_mask] = color

    def render(self, console: Console, context: Context) -> None:
        if self.player.is_alive:
            self._flicker_torch()
        else:
            self._update_floor_color((0, 0, 0))

        render_hp_bar(
            console=console,
            current_value=self.player.fighter.hp,
            maximum_value=self.player.fighter.max_hp,
        )

        render_names_at_mouse_location(
            console=console,
            engine=self,
            x=general.MESSAGE_LOG_X,
            y=general.MESSAGE_LOG_Y - 1,  # Place "look" details one above message log
        )

        self.message_log.render(
            console=console,
            x=general.MESSAGE_LOG_X,
            y=general.MESSAGE_LOG_Y,
            width=general.MESSAGE_LOG_WIDTH,
            height=general.MESSAGE_LOG_HEIGHT,
        )

        self.game_map.render(console)

        context.present(
            console,
            keep_aspect=True,
            integer_scaling=True,
            clear_color=colors.MAP_BORDER_COLOR,
        )

        console.clear()
