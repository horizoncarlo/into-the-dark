from components import consumable
from components.ai import HostileEnemy
from components.fighter import Fighter
from components.inventory import Inventory
from constants import colors
from entity import Actor, Entity, Item
from render_order import RenderOrder

stairs_up = Entity(
    char="<",
    fg_color=(150, 150, 170),
    bg_color=(105, 105, 105),
    name="Stairs up",
    render_order=RenderOrder.STAIRS,
)

# The heroic hero
player = Actor(
    char="☺",
    fg_color=colors.CORNFLOWER_RGB,
    bg_color=(0, 0, 0),
    name="Priest",
    ai_cls=HostileEnemy,
    light_radius=4,
    fighter=Fighter(hp=30, defense=2, power=5),
    inventory=Inventory(
        capacity=26
    ),  # Capacity is the length of the alphabet for the inventory window
)

# Items
healing_potion = Item(
    char="!",
    fg_color=(127, 0, 255),
    name="Potion - Healing",
    consumable=consumable.HealingConsumable(amount=4),
)
babel_scroll = Item(
    char="?",
    fg_color=(217, 48, 200),
    bg_color=(255, 255, 255),
    name="Scroll - Babel",
    consumable=consumable.BabelConsumable(number_of_turns=10),
)
holy_blast_scroll = Item(
    char="☼",
    fg_color=(200, 0, 0),
    bg_color=(255, 255, 255),
    name="Scroll - Holy Blast",
    consumable=consumable.HolyBlastConsumable(damage=12, radius=3),
)
sunbeam_scroll = Item(
    char="▼",
    fg_color=(204, 102, 0),
    bg_color=(255, 255, 255),
    name="Scroll - Sunbeam",
    consumable=consumable.SunbeamConsumable(damage=20, maximum_range=5),
)

# Monsters
orc = Actor(
    char="Ω",
    fg_color=(63, 127, 63),
    name="Orc",
    ai_cls=HostileEnemy,
    fighter=Fighter(hp=10, defense=0, power=3),
)
troll = Actor(
    char="☻",
    fg_color=(0, 240, 0),
    name="Troll",
    ai_cls=HostileEnemy,
    fighter=Fighter(hp=16, defense=1, power=4),
)
