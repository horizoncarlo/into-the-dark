import tcod
import numpy as np  # type: ignore

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

ROOM_MAX_SIZE = 10
ROOM_MIN_SIZE = 6
MAX_ROOMS = 50
MAX_MONSTERS_PER_ROOM = 2
MAX_ITEMS_PER_ROOM = 2

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
HP_BAR_Y = HEIGHT - 2
HP_BAR_WIDTH = 15
HP_BAR_HEIGHT = 1

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
