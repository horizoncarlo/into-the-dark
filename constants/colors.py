import random

GOLDENROD_RGB = (218, 165, 32)
CORNFLOWER_RGB = (100, 149, 237)

MAP_BORDER_COLOR = (random.randint(0, 50), random.randint(0, 50), random.randint(0, 50))

TORCH_BG_BASE = (150, 130, 0)
TORCH_FG_BASE = (80, 60, 0)
DEAD_BLOOD_FG_RGB = (190, 0, 0)
DEAD_BLOOD_BG_RGB = None

white = (255, 255, 255)
black = (0, 0, 0)
red = (255, 0, 0)
yellow = (255, 255, 0)
light_orange = (255, 213, 128)

player_atk = (200, 200, 230)
enemy_atk = (255, 192, 192)
needs_target = (63, 255, 255)
status_effect_applied = (63, 180, 63)
weapon = (100, 100, 100)

player_die = (255, 48, 48)
enemy_die = (255, 160, 48)

view_bg = (186, 85, 211)
view_fg = view_bg

invalid = (255, 255, 0)
impossible = (128, 128, 128)
error = (255, 64, 64)

hp_recovered = (0, 255, 0)
welcome_text = (32, 160, 255)

menu_text = white

hp_bar_text = white
hp_bar_filled = (0, 96, 0)
hp_bar_empty = (64, 16, 16)


def generate_color() -> tuple[int, int, int]:
    return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
