"""Handle the loading and initialization of game sessions."""

from __future__ import annotations

import copy
import lzma
import pickle
import random
import traceback
from typing import Optional

import tcod
from tcod import libtcodpy

import entity_factory
import input_handlers
from constants import colors, general
from engine import Engine
from game_map import GameWorld

# Load the background image and remove the alpha channel.
background_image = tcod.image.load("assets/menu_background.png")[:, :, :3]


def new_game() -> Engine:
    """Return a brand new game session as an Engine instance"""
    player = copy.deepcopy(entity_factory.player)

    #  Assign our default equipment
    dagger = copy.deepcopy(entity_factory.dagger)
    dagger.parent = player.inventory
    player.inventory.items.append(dagger)
    player.equipment.toggle_equip(dagger, add_message=False)

    vestments = copy.deepcopy(entity_factory.vestments)
    vestments.parent = player.inventory
    player.inventory.items.append(vestments)
    player.equipment.toggle_equip(vestments, add_message=False)

    engine = Engine(player=player)

    engine.game_world = GameWorld(
        engine=engine,
        max_rooms=general.MAX_ROOMS,
        room_min_size=general.ROOM_MIN_SIZE,
        room_max_size=general.ROOM_MAX_SIZE,
        map_width=general.MAP_WIDTH,
        map_height=general.MAP_HEIGHT,
    )
    engine.game_world.generate_floor()

    engine.message_log.add_message(
        random.choice(general.WELCOME_MESSAGES),
        colors.welcome_text,
    )
    return engine


def load_game(filename: str) -> Engine:
    """Load an Engine instance from a file"""
    with open(filename, "rb") as f:
        engine = pickle.loads(lzma.decompress(f.read()))
    assert isinstance(engine, Engine)
    return engine


class MainMenu(input_handlers.BaseEventHandler):
    """Handle the main menu rendering and input"""

    def on_render(
        self, console: tcod.console.Console, context: tcod.context.Context
    ) -> None:
        """Render the main menu on a background image"""
        console.draw_semigraphics(background_image, 0, 0)

        console.print(
            console.width // 2,
            1,
            """╠═╦═╣ ╔╗   ╦ ╠═╦═╣ ╔═══╗
  ║   ║╚╗☺ ║   ║   ║   ║
  ║   ║ ╚╗ ║   ║   ║   ║
  ║   ║  ╚╗║   ║   ║   ║
╠═╩═╣ ╩   ╚╝   ╩   ╚═══╝""",
            fg=(255, 255, 63),
            alignment=libtcodpy.CENTER,
        )
        console.print(
            console.width // 2,
            7,
            """╠═╦═╣ ╦   ╦ ╔══╣
  ║   ║   ║ ║   
  ║   ╠═══╣ ╠══╣
  ║   ║   ║ ║   
  ╩   ╩   ╩ ╚══╣""",
            fg=(204, 204, 50),
            alignment=libtcodpy.CENTER,
        )
        console.print(
            console.width // 2,
            13,
            """╔══╗   ╔═╗  ╔══╗  ╦   ╦
║  ╚╗ ╔╝ ╚╗ ║  ╚╗ ║  ╔╝
║   ║ ╠═══╣ ╠══╦╝ ╠══╬ 
║  ╔╝ ║   ║ ║  ╚╗ ║  ╚╗
╚══╝  ╩   ╩ ╩   ╩ ╩   ╩""",
            fg=(153, 153, 38),
            alignment=libtcodpy.CENTER,
        )
        console.print(
            console.width // 2,
            console.height - 2,
            "By Carlo Guglielmin ♣",
            fg=colors.welcome_text,
            alignment=libtcodpy.CENTER,
        )

        menu_width = 24
        for i, text in enumerate(["[N]ew game", "[L]oad game", "[Q]uit"]):
            console.print(
                console.width // 2,
                console.height // 2 - 2 + i,
                text.ljust(menu_width),
                fg=colors.menu_text,
                bg=colors.black,
                alignment=libtcodpy.CENTER,
                bg_blend=libtcodpy.BKGND_ALPHA(64),
            )

    def ev_keydown(
        self, event: tcod.event.KeyDown
    ) -> Optional[input_handlers.BaseEventHandler]:
        if event.sym in (tcod.event.KeySym.Q, tcod.event.KeySym.ESCAPE):
            raise SystemExit()
        elif event.sym == tcod.event.KeySym.L:
            try:
                return input_handlers.MainGameEventHandler(load_game(general.SAVE_FILE))
            except FileNotFoundError:
                return input_handlers.PopupMessage(self, "No saved game to load")
            except Exception as exc:
                traceback.print_exc()  # Print to stderr
                return input_handlers.PopupMessage(self, f"Failed to load save:\n{exc}")
        elif event.sym == tcod.event.KeySym.N:
            return input_handlers.MainGameEventHandler(new_game())

        return None
