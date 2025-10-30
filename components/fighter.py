from __future__ import annotations

from typing import TYPE_CHECKING

from components.base_component import BaseComponent
from constants import colors
from render_order import RenderOrder

if TYPE_CHECKING:
    from entity import Actor


class Fighter(BaseComponent):
    parent: Actor

    def __init__(self, hp: int, base_defense: int, base_power: int):
        self.max_hp = hp
        self._hp = hp
        self.base_defense = base_defense
        self.base_power = base_power

    @property
    def hp(self) -> int:
        return self._hp

    @hp.setter
    def hp(self, value: int) -> None:
        self._hp = max(0, min(value, self.max_hp))
        if self._hp == 0 and self.parent.ai:
            self.die()

    @property
    def defense(self) -> int:
        return self.base_defense + self.defense_bonus

    @property
    def power(self) -> int:
        return self.base_power + self.power_bonus

    @property
    def defense_bonus(self) -> int:
        return self.parent.equipment.defense_bonus if self.parent.equipment else 0

    @property
    def power_bonus(self) -> int:
        return self.parent.equipment.power_bonus if self.parent.equipment else 0

    def heal(self, amount: int) -> int:
        if self.hp == self.max_hp:
            return 0

        new_hp_value = max(self.hp + amount, self.max_hp)
        amount_recovered = new_hp_value - self.hp

        self.hp = new_hp_value

        return amount_recovered

    def take_damage(self, amount: int) -> None:
        self.hp -= amount

    def die(self) -> None:
        if self.engine.player is self.parent:
            # TODO Popup death message as well as a chat log
            death_message = "You died! Better luck next time."
            death_message_color = colors.player_die
        else:
            death_message = f"{self.parent.name} is dead!"
            death_message_color = colors.enemy_die
            self.parent.char = "≈"

        self.parent.fg_color = colors.DEAD_BLOOD_FG_RGB
        self.parent.bg_color = colors.DEAD_BLOOD_BG_RGB
        self.parent.blocks_movement = False
        self.parent.render_order = RenderOrder.CORPSE
        self.parent.ai = None
        self.parent.name = f"remains of {self.parent.name}"
        self.parent.light_radius = 1

        self.engine.message_log.add_message(death_message, death_message_color)

        if self.parent.level.xp_given > 0:
            self.engine.player.level.add_xp(self.parent.level.xp_given)
