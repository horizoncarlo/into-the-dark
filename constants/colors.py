import random

GOLDENROD_RGB = (218, 165, 32)
CORNFLOWER_RGB = (100, 149, 237)

MAP_BORDER_COLOR = (random.randint(0, 50), random.randint(0, 50), random.randint(0, 50))

FLOOR_FG_RGB = (30, 30, 50)
FLOOR_BG_RGB = (20, 20, 20)
WALL_FG_RGB = (40, 40, 60)
WALL_BG_RGB = (80, 80, 80)

TORCH_BASE_RGB = (150, 130, 0)
DEAD_BLOOD_FG_RGB = (190, 0, 0)
DEAD_BLOOD_BG_RGB = None

white = (255, 255, 255)
black = (0, 0, 0)

player_atk = (224, 224, 224)
enemy_atk = (255, 192, 192)

player_die = (255, 48, 48)
enemy_die = (255, 160, 48)

view_bg = (186, 85, 211)
view_fg = view_bg
welcome_text = (32, 160, 255)

bar_text = white
bar_filled = (0, 96, 0)
bar_empty = (64, 16, 16)
