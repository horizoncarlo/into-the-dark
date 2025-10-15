import colors

from entity import Entity

player = Entity(char="☺", color=colors.GOLDENROD_RGB, name="Player", light_radius=4, blocks_movement=True)

orc = Entity(char="Ω", color=(63, 127, 63), name="Orc", blocks_movement=True)
troll = Entity(char="☻", color=(0, 240, 0), name="Troll", blocks_movement=True)