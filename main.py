#!/usr/bin/env python3

import copy
import tcod
import time
import entity_factory

from engine import Engine
from gen_map import generate_dungeon
from constants import colors, general

# Can play with SDL rendering quality
# os.environ["SDL_RENDER_SCALE_QUALITY"] = "best"

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
    engine = Engine(player=player)

    engine.game_map = generate_dungeon(
        max_rooms=general.MAX_ROOMS,
        room_min_size=general.ROOM_MIN_SIZE,
        room_max_size=general.ROOM_MAX_SIZE,
        map_width=general.MAP_WIDTH,
        map_height=general.MAP_HEIGHT,
        max_monsters_per_room=general.MAX_MONSTERS_PER_ROOM,
        engine=engine
    )
    engine.update_fov()

    engine.message_log.add_message(
        "Hello and welcome, adventurer, to yet another dungeon!", colors.welcome_text # TTODO Intro message
    )

    with tcod.context.new(
        columns=general.WIDTH,
        rows=general.HEIGHT,
        sdl_window_flags=general.SDL_FLAGS,
        tileset=tileset,
        title="Into the Dark",
        vsync=True,
    ) as context:
        # Roughly resize to the recommended amount to fit the screen. We likely want a fixed play area for balance though
        # rec_width, rec_height = context.recommended_console_size()
        # root_console = tcod.console.Console(rec_width+1, rec_height, order="F")

        root_console = tcod.console.Console(general.WIDTH, general.HEIGHT, order="F")
        frame_duration = 1 / general.FPS
        last_frame = time.time()

        while True:
            now = time.time()

            engine.event_handler.handle_events(tcod.event.get())

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
