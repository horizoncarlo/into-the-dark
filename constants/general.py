import tcod

FPS = 30


# Increasing the size values will "zoom out" on the content
WIDTH, HEIGHT = 79, 48 # Manually done for 1080p

HUD_SIZE = 5
MAP_WIDTH, MAP_HEIGHT = WIDTH, HEIGHT - HUD_SIZE

ROOM_MAX_SIZE = 10
ROOM_MIN_SIZE = 6
MAX_ROOMS = 50
MAX_MONSTERS_PER_ROOM = 2

# TODO Start fullscreen (for now just maximized as it's easier to debug)
SDL_FLAGS = tcod.context.SDL_WINDOW_RESIZABLE | tcod.context.SDL_WINDOW_MAXIMIZED #| tcod.context.SDL_WINDOW_FULLSCREEN

TORCH_FLICKER_INTERVAL_MIN = 0.05
TORCH_FLICKER_INTERVAL_MAX = 0.5
TORCH_FLICKER_COLOR_MIN = -20
TORCH_FLICKER_COLOR_MAX = 25