from __future__ import annotations

import math
import random
from typing import Iterable, Iterator, Optional, TYPE_CHECKING

import numpy as np  # type: ignore
from tcod.console import Console

import tile_types
from constants import colors, general
from entity import Actor, Item

if TYPE_CHECKING:
    from engine import Engine
    from entity import Entity


class GameMap:
    def __init__(
        self, engine: Engine, width: int, height: int, entities: Iterable[Entity] = ()
    ):
        self.engine = engine
        self.width, self.height = width, height
        self.entities = set(entities)
        self.tiles = np.full((width, height), fill_value=tile_types.wall, order="F")

        self.visible = np.full(
            (width, height), fill_value=False, order="F"
        )  # Tiles the player can currently see
        self.explored = np.full(
            (width, height), fill_value=False, order="F"
        )  # Tiles the player has seen before

        self.downstairs_location = (0, 0)

    @property
    def game_map(self) -> GameMap:
        return self

    @property
    def actors(self) -> Iterator[Actor]:
        """Iterate over this maps living actors"""
        yield from (
            entity
            for entity in self.entities
            if isinstance(entity, Actor) and entity.is_alive
        )

    @property
    def items(self) -> Iterator[Item]:
        yield from (entity for entity in self.entities if isinstance(entity, Item))

    def get_entity_at_location(self, x: int, y: int) -> Optional[Entity]:
        for entity in self.entities:
            if entity.x == x and entity.y == y:
                return entity
        return None

    def get_blocking_entity_at_location(
        self,
        location_x: int,
        location_y: int,
    ) -> Optional[Entity]:
        for entity in self.entities:
            if (
                entity.blocks_movement
                and entity.x == location_x
                and entity.y == location_y
            ):
                return entity
        return None

    def get_actor_at_location(self, x: int, y: int) -> Optional[Actor]:
        for actor in self.actors:
            if actor.x == x and actor.y == y:
                return actor
        return None

    def in_bounds(self, x: int, y: int) -> bool:
        """Return True if x and y are inside of the bounds of this map"""
        return 0 <= x < self.width and 0 <= y < self.height

    def render(self, console: Console) -> None:
        """
        Renders the map

        If a tile is in the "visible" array, then draw it with the "light" colors
        If it isn't, but it's in the "explored" array, then draw it with the "dark" colors
        Otherwise, the default is the fog of war
        """
        console.rgb[0 : self.width, 0 : self.height] = np.select(
            condlist=[self.visible, self.explored],
            choicelist=[self.tiles["light"], self.tiles["dark"]],
            default=(
                self.tiles["dark"]
                if general.DEBUG_NO_FOG_OF_WAR or self.engine.show_entire_map
                else general.FOG_OF_WAR
            ),
        )

        entities_sorted_for_rendering = sorted(
            self.entities, key=lambda x: x.render_order.value
        )

        for entity in entities_sorted_for_rendering:
            # Only print entities that are in the FOV
            if self.visible[entity.x, entity.y]:
                console.print(
                    x=entity.x,
                    y=entity.y,
                    string=entity.char,
                    fg=entity.fg_color,
                    bg=entity.bg_color,
                )


class GameWorld:
    """
    Holds the settings for the GameMap, and generates new maps when moving down the stairs
    """

    def __init__(
        self,
        *,
        engine: Engine,
        current_floor: int = 0,
    ):
        self.engine = engine
        self.current_floor = current_floor

    def generate_floor(self) -> None:
        from gen_map import generate_dungeon

        self.current_floor += 1
        self.engine.show_entire_map = False

        # Customize how our tiles look (symbols and colors)
        tile_types.generate_tiles()
        map_width = general.WIDTH
        map_height = general.HEIGHT - general.HUD_SIZE

        # Note for the room cap, if a room intersects we skip it, so it's okay to have a potential lot here
        max_rooms = math.ceil(map_width * map_height / random.randint(5, 80))
        room_min_size = random.randint(2, 6)
        room_max_size = room_min_size + random.randint(2, 5)

        # Some of the crazier options only happen after they have a normal floor, to give a bit of a fair/consistent start
        if self.current_floor > 1:
            # Have a chance for a smaller map after the first floor
            if random.random() > 0.75:
                map_width = random.randint(general.WIDTH // 4, general.WIDTH)
                map_height = max(
                    random.randint(general.HEIGHT // 4, general.HEIGHT)
                    - general.HUD_SIZE,
                    general.HUD_SIZE * 2,
                )

            # Sometimes get no fog of war...black sheep wall
            if random.random() > 0.9:
                self.engine.message_log.add_message(
                    "You are BLESSED with divine sight", colors.yellow
                )
                self.engine.show_entire_map = True

            # TODO Randomize our light radius per floor for fun - should eventually dwindle over time as a resource?
            # And of course the chance for something REALLY wild, that almost looks like a bug haha
            if random.random() > 0.95:
                self.engine.player.light_radius = random.randint(10, 20)
            else:
                self.engine.player.light_radius = random.randint(2, 5)

        self.engine.make_new_bar_color()

        self.engine.game_map = generate_dungeon(
            max_rooms=max_rooms,
            room_min_size=room_min_size,
            room_max_size=room_max_size,
            map_width=map_width,
            map_height=map_height,
            engine=self.engine,
        )

        self.engine.update_fov()
