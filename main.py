#!/usr/bin/env python3
import tcod

from engine import Engine
from entity import Entity
from gen_map import generate_dungeon
from input_handlers import EventHandler

# Increasing the size values will "zoom out" on the content
HUD_SIZE = 5
WIDTH, HEIGHT = 75, 40
MAP_WIDTH, MAP_HEIGHT = WIDTH, HEIGHT - HUD_SIZE

ROOM_MAX_SIZE = 10
ROOM_MIN_SIZE = 6
MAX_ROOMS = 50

# Legal requirement
GOLDENROD_RGB = [218, 165, 32]
CORNFLOWER_RGB = [100, 149, 237]

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

    player = Entity(int(WIDTH / 2), int(HEIGHT / 2), "☺", GOLDENROD_RGB)
    npc = Entity(int(WIDTH / 2 - 5), int(HEIGHT / 2), "☻", CORNFLOWER_RGB)
    entities = {npc, player}

    game_map = generate_dungeon(
        max_rooms=MAX_ROOMS,
        room_min_size=ROOM_MIN_SIZE,
        room_max_size=ROOM_MAX_SIZE,
        map_width=MAP_WIDTH,
        map_height=MAP_HEIGHT,
        player=player
    )

    engine = Engine(entities, event_handler, game_map, player)

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

        while True:
            engine.render(root_console, context)

            events = tcod.event.wait()

            engine.handle_events(events)

            # Alternative approach from TCOD doc tutorial, nice part is the magnification
            # console = context.new_console(magnification=2)
            # console.print(x=1, y=10, string="@")
            # context.present(console, keep_aspect=True, integer_scaling=True)

if __name__ == "__main__":
    main()
