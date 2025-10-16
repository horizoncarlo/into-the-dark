import random

GOLDENROD_RGB = [218, 165, 32]
CORNFLOWER_RGB = [100, 149, 237]

MAP_BORDER_COLOR = [random.randint(0, 50), random.randint(0, 50), random.randint(0, 50)]

FLOOR_FG_RGB = (30, 30, 50)
FLOOR_BG_RGB = (20, 20, 20)
WALL_FG_RGB = (40, 40, 60)
WALL_BG_RGB = (80, 80, 80)

TORCH_BASE_RGB = (150, 130, 0)
DEAD_BLOOD_FG_RGB = (190, 0, 0)
DEAD_BLOOD_BG_RGB = None

white = (0xFF, 0xFF, 0xFF)
black = (0x0, 0x0, 0x0)

player_atk = (0xE0, 0xE0, 0xE0)
enemy_atk = (0xFF, 0xC0, 0xC0)

player_die = (0xFF, 0x30, 0x30)
enemy_die = (0xFF, 0xA0, 0x30)

welcome_text = (0x20, 0xA0, 0xFF)

bar_text = white
bar_filled = (0x0, 0x60, 0x0)
bar_empty = (0x40, 0x10, 0x10)
