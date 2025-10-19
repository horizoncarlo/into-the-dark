#!/usr/bin/env python3

import copy
import random

import tcod

import entity_factory
from constants import colors, general
from engine import Engine
from exceptions import StopRendering, StartRendering, ImpossibleAction
from gen_map import generate_dungeon


# Can play with SDL rendering quality
# os.environ["SDL_RENDER_SCALE_QUALITY"] = "best"


def main() -> None:
    # TODO Decide on a font/tileset, and likely allow customization
    # tileset = tcod.tileset.load_tilesheet("assets/dejavu10x10_gs_tc.png", 32, 8, tcod.tileset.CHARMAP_TCOD)
    # tileset = tcod.tileset.load_truetype_font("assets/cp437-12x24.ttf", 12, 24)
    # tileset = tcod.tileset.load_truetype_font("assets/dungeon-mode.ttf", 16, 16)
    tileset = tcod.tileset.load_tilesheet(
        "assets/Zesty_curses_24x24.png", 16, 16, tcod.tileset.CHARMAP_CP437
    )
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
        max_items_per_room=general.MAX_ITEMS_PER_ROOM,
        engine=engine,
    )
    engine.update_fov()

    engine.message_log.add_message(
        random.choice(general.WELCOME_MESSAGES),
        colors.welcome_text,
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

        while True:
            root_console.clear()
            engine.event_handler.on_render(console=root_console, context=context)
            try:
                engine.event_handler.handle_events(
                    context=context, events=tcod.event.wait()
                )
            except (StopRendering, StartRendering):  # From torch flicker approach
                pass
            except ImpossibleAction as ia:
                engine.message_log.add_error(str(ia))

        # # TODO This approach allows for a torch flicker independent from the player movement (using .get instead of .wait)
        # # But it causes some hassles for non-map windows (like HistoryViewer) that would get overwritten by re-renders
        # # Way fancier version in the tcod samples: https://github.com/libtcod/python-tcod/blob/develop/examples/samples_tcod.py
        # frame_duration = 1 / general.FPS
        # last_frame = time.time()
        # is_paused = False
        #
        # while True:
        #     now = time.time()
        #
        #     # Render loop MIGHT not be the cleanest, but hey it's our first try
        #     # Idea is we loop at FPS speed to get a reliable torch flicker and still accept user input
        #     # Then if we have a paused screen, such as opening HistoryViewer, then we stop redrawing until done
        #     if not is_paused:
        #         if now - last_frame >= frame_duration:
        #             last_frame = now
        #             engine.event_handler.on_render(root_console, context)
        #
        #         time.sleep(max(0, frame_duration - (time.time() - now)))
        #
        #         try:
        #             engine.event_handler.handle_events(context, tcod.event.get())
        #         except StopRendering:
        #             is_paused = True
        #     else:
        #         # At this point we have HistoryViewer (or another "blocking" task via StopRendering exception)
        #         # So we render that and instead of .get we pause the loop with .wait
        #         try:
        #             engine.event_handler.on_render(
        #                 console=root_console, context=context
        #             )
        #             engine.event_handler.handle_events(
        #                 context=context, events=tcod.event.wait()
        #             )
        #         except StartRendering:
        #             is_paused = False

        # Alternative approach from TCOD doc tutorial, nice part is the magnification
        # console = context.new_console(magnification=2)
        # console.print(x=1, y=10, string="@")
        # context.present(console, keep_aspect=True, integer_scaling=True)


if __name__ == "__main__":
    main()
