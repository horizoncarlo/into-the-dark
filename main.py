#!/usr/bin/env python3

import copy
import tcod
import time
import entity_factory

from engine import Engine
from entity import Entity
from gen_map import generate_dungeon
from input_handlers import EventHandler

FPS = 30

# Increasing the size values will "zoom out" on the content
HUD_SIZE = 5
# WIDTH, HEIGHT = 75, 40
WIDTH, HEIGHT = 79, 48
MAP_WIDTH, MAP_HEIGHT = WIDTH, HEIGHT - HUD_SIZE

ROOM_MAX_SIZE = 10
ROOM_MIN_SIZE = 6
MAX_ROOMS = 50
MAX_MONSTERS_PER_ROOM = 2

# TODO Start fullscreen (for now just maximized as it's easier to debug)
FLAGS = tcod.context.SDL_WINDOW_RESIZABLE | tcod.context.SDL_WINDOW_MAXIMIZED #| tcod.context.SDL_WINDOW_FULLSCREEN

# Can play with SDL rendering quality
# os.environ["SDL_RENDER_SCALE_QUALITY"] = "best"

event_handler = EventHandler()

def main() -> None:
    # TODO Decide on a font/tileset, and likely allow customization
    # tileset = tcod.tileset.load_tilesheet("assets/dejavu10x10_gs_tc.png", 32, 8, tcod.tileset.CHARMAP_TCOD)
    # tileset = tcod.tileset.load_truetype_font("assets/cp437-12x24.ttf", 12, 24)
    # tileset = tcod.tileset.load_truetype_font("assets/dungeon-mode.ttf", 16, 16)
    tileset = tcod.tileset.load_tilesheet("assets/Zesty_curses_24x24.png", 16, 16, tcod.tileset.CHARMAP_CP437)
    # tileset = tcod.tileset.load_tilesheet("assets/Tahin_16x16_rounded.png", 16, 16, tcod.tileset.CHARMAP_CP437)
    # tileset = tcod.tileset.load_tilesheet("assets/Nagidal24x24shade.png", 16, 16, tcod.tileset.CHARMAP_CP437)
    # tileset = tcod.tileset.load_tilesheet("assets/Runeset_24x24.png", 16, 16, tcod.tileset.CHARMAP_CP437)
    # tileset = tcod.tileset.load_tilesheet("assets/Teeto_K_18x18.png", 16, 16, tcod.tileset.CHARMAP_CP437)

    player = copy.deepcopy(entity_factory.player)

    game_map = generate_dungeon(
        max_rooms=MAX_ROOMS,
        room_min_size=ROOM_MIN_SIZE,
        room_max_size=ROOM_MAX_SIZE,
        map_width=MAP_WIDTH,
        map_height=MAP_HEIGHT,
        max_monsters_per_room=MAX_MONSTERS_PER_ROOM,
        player=player
    )

    engine = Engine(event_handler, game_map, player)

    with tcod.context.new(
        columns=WIDTH,
        rows=HEIGHT,
        sdl_window_flags=FLAGS,
        tileset=tileset,
        title="Into the Dark",
        vsync=True,
    ) as context:
        # Roughly resize to the recommended amount to fit the screen. We likely want a fixed play area for balance though
        # rec_width, rec_height = context.recommended_console_size()
        # root_console = tcod.console.Console(rec_width+1, rec_height, order="F")

        root_console = tcod.console.Console(WIDTH, HEIGHT, order="F")
        frame_duration = 1 / FPS
        last_frame = time.time()

        while True:
            now = time.time()

            events = list(tcod.event.get())
            if events:
                engine.handle_events(events)

            if now - last_frame >= frame_duration:
                last_frame = now
                engine.render(root_console, context)

            time.sleep(max(0, frame_duration - (time.time() - now)))

        # Original tutorial code, replaced when we wanted to mess around with torch flickering (done in engine)
        # while True:
        #     engine.render(root_console, context)
        #
        #     events = tcod.event.wait()
        #
        #     engine.handle_events(events)
        #
        #     # Alternative approach from TCOD doc tutorial, nice part is the magnification
        #     # console = context.new_console(magnification=2)
        #     # console.print(x=1, y=10, string="@")
        #     # context.present(console, keep_aspect=True, integer_scaling=True)

if __name__ == "__main__":
    main()
