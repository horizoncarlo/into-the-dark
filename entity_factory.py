from constants import colors

from components.ai import HostileEnemy
from components.fighter import Fighter
from entity import Actor

# The heroic hero
player = Actor(
    char="☺",
    color=colors.GOLDENROD_RGB,
    name="Player",
    ai_cls=HostileEnemy,
    light_radius=4,
    fighter=Fighter(hp=30, defense=2, power=5),
)

# Monsters
orc = Actor(
    char="Ω",
    color=(63, 127, 63),
    name="Orc",
    ai_cls=HostileEnemy,
    fighter=Fighter(hp=10, defense=0, power=3),
)
troll = Actor(
    char="☻",
    color=(0, 240, 0),
    name="Troll",
    ai_cls=HostileEnemy,
    fighter=Fighter(hp=16, defense=1, power=4),
)