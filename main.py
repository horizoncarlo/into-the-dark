#!/usr/bin/env python3

import traceback

import tcod

import exceptions
import input_handlers
import setup_game
from constants import colors, general
from exceptions import ImpossibleAction


# Can play with SDL rendering quality
# os.environ["SDL_RENDER_SCALE_QUALITY"] = "best"


def save_game(handler: input_handlers.BaseEventHandler) -> None:
    """If the current event handler has an active Engine then save it"""
    if isinstance(handler, input_handlers.EventHandler):
        handler.engine.save_as(general.SAVE_FILE)
        print("Game saved")


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

    handler: input_handlers.BaseEventHandler = setup_game.MainMenu()

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

        try:
            while True:
                root_console.clear()

                handler.on_render(console=root_console, context=context)

                context.present(
                    root_console,
                    keep_aspect=True,
                    integer_scaling=True,
                    clear_color=colors.MAP_BORDER_COLOR,
                )

                try:
                    for event in tcod.event.wait():
                        context.convert_event(event)
                        handler = handler.handle_event(event)
                except ImpossibleAction as ia:
                    if isinstance(handler, input_handlers.EventHandler):
                        handler.engine.message_log.add_error(str(ia))
                except Exception:  # Handle exceptions in game.
                    traceback.print_exc()  # Print error to stderr.
                    # Then print the error to the message log.
                    if isinstance(handler, input_handlers.EventHandler):
                        handler.engine.message_log.add_message(
                            traceback.format_exc(), colors.error
                        )
        except exceptions.QuitWithoutSaving:
            raise
        except SystemExit:  # Save and quit
            save_game(handler)
            raise
        except BaseException:  # Save on any other unexpected exception
            save_game(handler)
            raise


if __name__ == "__main__":
    main()
