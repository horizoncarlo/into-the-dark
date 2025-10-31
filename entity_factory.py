from components import consumable
from components import equippable
from components.ai import HostileEnemy
from components.equipment import Equipment
from components.fighter import Fighter
from components.inventory import Inventory
from components.level import Level
from constants import colors
from entity import Actor, Entity, Item
from render_order import RenderOrder

# TODO Do stairs_up like the down_stairs in tile_types, including showing through fog of war
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
    fighter=Fighter(hp=30, base_defense=1, base_power=2),
    level=Level(level_up_base=200),
    inventory=Inventory(
        capacity=26
    ),  # Capacity is the length of the alphabet for the inventory window
    equipment=Equipment(),
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
    bg_color=colors.white,
    name="Scroll - Babel",
    consumable=consumable.BabelConsumable(number_of_turns=10),
)
reckoning_scroll = Item(
    char="☼",
    fg_color=colors.red,
    bg_color=colors.white,
    name="Scroll - Reckoning",
    consumable=consumable.ReckoningConsumable(damage=12, radius=3),
)
holy_blast_scroll = Item(
    char="┼",
    fg_color=(200, 200, 0),
    bg_color=colors.white,
    name="Scroll - Holy Blast",
    consumable=consumable.HolyBlastConsumable(char="┼", damage=15),
)
sunbeam_scroll = Item(
    char="▼",
    fg_color=(204, 102, 0),
    bg_color=colors.white,
    name="Scroll - Sunbeam",
    consumable=consumable.SunbeamConsumable(damage=20, maximum_range=5),
)

# Equipment
dagger = Item(
    char="/",
    fg_color=(0, 191, 255),
    bg_color=(0, 0, 104),
    name="Dagger",
    equippable=equippable.Dagger(),
)

cudgel = Item(
    char="/",
    fg_color=(0, 191, 255),
    bg_color=(0, 0, 104),
    name="Cudgel",
    equippable=equippable.Cudgel(),
)

vestments = Item(
    char="[",
    fg_color=(139, 69, 19),
    bg_color=(0, 0, 104),
    name="Vestments",
    equippable=equippable.Vestments(),
)

chain_mail = Item(
    char="[",
    fg_color=(139, 69, 19),
    bg_color=(0, 0, 104),
    name="Chain Mail",
    equippable=equippable.ChainMail(),
)

# Monsters
orc = Actor(
    char="Ω",
    fg_color=(63, 127, 63),
    name="Orc",
    ai_cls=HostileEnemy,
    fighter=Fighter(hp=10, base_defense=0, base_power_min=2, base_power=4),
    level=Level(xp_given=35),
)
troll = Actor(
    char="☻",
    fg_color=(0, 240, 0),
    name="Troll",
    ai_cls=HostileEnemy,
    fighter=Fighter(hp=16, base_defense=1, base_power_min=3, base_power=5),
    level=Level(xp_given=100),
)
