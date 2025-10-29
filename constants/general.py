from typing import TYPE_CHECKING

import numpy as np  # type: ignore
import tcod

if TYPE_CHECKING:
    pass

# TODO IDEAS:
# Real time "action commands" for attack/defense
# More interesting stat system as a result
# Bosses
# Different colored tiles per floor
# Different map gen params per floor (some are a few huge rooms, others are tight small rooms, etc.)
# Max floor to reach? Or just scale infinitely?
# Scroll (Item) to show map (toggle fog of war for a render window)
# More enemies (duh), including DOTs like poison
# Momentum style push back on attack?
# Pillars, doors, chasms, water, other room gen features (would be more types of tiles)
# Change healing potions to some kind of MP based spell? They're really boring at the moment
# More RANDOM stuff, including enemy HP and so on, floors currently (obviously) feel hecka samey

DEBUG_NO_FOG_OF_WAR = False

SAVE_FILE = "into_the_dark.sav"
FPS = 30

WELCOME_MESSAGES = [
    "Torchlight flickers as the monastery doors close behind you",
    "Darkness envelops the dusty corridors of the monastery",
    "Your footsteps echo through the empty monastery",
    "You descend the monastery stairs with uncertainty",
]

# Increasing the size values will "zoom out" on the content
WIDTH, HEIGHT = 79, 48  # Manually done for 1080p
HUD_SIZE = 5
MAP_WIDTH, MAP_HEIGHT = WIDTH, HEIGHT - HUD_SIZE

# TODO Playing with the room count and size really changes the dungeon (...obviously)
# Realistically won't even be close on the room cap, since if a room intersects we skip it
MAX_ROOMS = 200
ROOM_MAX_SIZE = 9
ROOM_MIN_SIZE = 4

# TODO Start fullscreen (for now just maximized as it's easier to debug)
SDL_FLAGS = (
    tcod.context.SDL_WINDOW_RESIZABLE
    | tcod.context.SDL_WINDOW_MAXIMIZED  # | tcod.context.SDL_WINDOW_FULLSCREEN
)

TORCH_FLICKER_INTERVAL_MIN = 0.05
TORCH_FLICKER_INTERVAL_MAX = 0.5
TORCH_FLICKER_COLOR_MIN = -20
TORCH_FLICKER_COLOR_MAX = 25

HP_BAR_X = 1
HP_BAR_Y = HEIGHT - HUD_SIZE
HP_BAR_WIDTH = 15
HP_BAR_HEIGHT = 1

DUNGEON_LVL_X = 1
DUNGEON_LVL_Y = HEIGHT - HUD_SIZE + 1

MESSAGE_LOG_X = HP_BAR_WIDTH + 2
MESSAGE_LOG_Y = HEIGHT - HUD_SIZE + 1
MESSAGE_LOG_WIDTH = WIDTH - HP_BAR_WIDTH - 1
MESSAGE_LOG_HEIGHT = 4

# Tile graphics structured type compatible with Console.tiles_rgb
GRAPHIC_DT = np.dtype(
    [
        ("ch", np.int32),  # Unicode codepoint
        ("fg", "3B"),  # 3 unsigned bytes, for RGB colors
        ("bg", "3B"),
    ]
)

FOG_OF_WAR = np.array((ord(" "), (255, 255, 255), (0, 0, 0)), dtype=GRAPHIC_DT)
