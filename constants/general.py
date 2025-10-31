from typing import TYPE_CHECKING

import numpy as np  # type: ignore
import tcod

if TYPE_CHECKING:
    pass

# TODO NEXT:
# Make all weapon fill be based on equipped weapon, and start with a random different weapon

# TODO IDEAS:
# More interesting stat system, perhaps can modify how weapon fill timing works?
# Bosses
# Max floor to reach? Or just scale infinitely?
# Scroll (Item) to show map (toggle fog of war for a render window)
# More enemies (duh), including DOTs like poison
# Momentum style push back on attack?
# Pillars, doors, chasms, water, other room gen features (would be more types of tiles)
# Change healing potions to some kind of MP based spell? They're really boring at the moment
# Spells and MP in general, can try to learn a scroll instead of using it? Then have access to it forever. Likely need to scale (aka weaken) spells accordingly
# Game timer for high scores? And a scoreboard in general
# More RANDOM stuff, including enemy HP/damage and so on, room contents currently (obviously) feel hecka samey
# Undead and Turning undead concepts
# Very very simple initial character choices? Changes stats, HP, equipment, etc.
# Choose your own character icon color (foreground AND background?)
# Stances like Aggressive or Defensive that build over time (rewarding keeping them on and planning and not switching). Most have a downside. Do nothing the first turn they're switched?
# Charge you target enemies with a skill, also builds up over time
# Enemies that punish the player for waiting, like they charge in or shoot? Only when the player actually waits
# Doors on rooms
# Go to orthagonal movement only with no diagonals?
# Torches that dwindle down the light radius over time
# Holy Symbol a fallback option (1 or 2 squares radius), would be a different color
# Directional armed Shield you can hold - slower movement but defensive bonus or damage reduction?
# Add a help that shows all keys. Also show on start screen menu. Maybe have an Instructions window too

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
WIDTH, HEIGHT = 80, 45  # Manually done for 1080p
HUD_SIZE = 4

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
DUNGEON_LVL_Y = HP_BAR_Y + 1

MESSAGE_LOG_X = HP_BAR_WIDTH + 2
MESSAGE_LOG_Y = HEIGHT - HUD_SIZE
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
