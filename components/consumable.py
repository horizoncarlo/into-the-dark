from __future__ import annotations

from typing import Optional, TYPE_CHECKING

import actions
import components.ai
import components.inventory
from components.base_component import BaseComponent
from constants import colors
from exceptions import ImpossibleAction
from input_handlers import (
    SingleRangedAttackHandler,
    CrossRangedAttackHandler,
    AreaRangedAttackHandler,
)

if TYPE_CHECKING:
    from entity import Actor, Item


class Consumable(BaseComponent):
    parent: Item

    def get_action(self, consumer: Actor) -> Optional[actions.Action]:
        """Try to return the action for this item"""
        return actions.ItemAction(consumer, self.parent)

    def activate(self, action: actions.ItemAction) -> None:
        """Invoke this items ability

        `action` is the context for this activation
        """
        raise NotImplementedError()

    def consume(self) -> None:
        """Remove the consumed item from its containing inventory"""
        entity = self.parent
        inventory = entity.parent
        if isinstance(inventory, components.inventory.Inventory):
            inventory.items.remove(entity)


class HealingConsumable(Consumable):
    def __init__(self, amount: int):
        self.amount = amount

    def activate(self, action: actions.ItemAction) -> None:
        consumer = action.entity
        amount_recovered = consumer.fighter.heal(self.amount)

        if amount_recovered > 0:
            self.engine.message_log.add_message(
                f"The potion warms your body and soothes your wounds, recovering {amount_recovered} HP!",
                colors.hp_recovered,
            )
            self.consume()
        else:
            raise ImpossibleAction(f"Your HP is already full")


class BabelConsumable(Consumable):
    def __init__(self, number_of_turns: int):
        self.number_of_turns = number_of_turns

    def get_action(self, consumer: Actor) -> Optional[actions.Action]:
        self.engine.message_log.add_message(
            "Select a target location", colors.needs_target
        )
        self.engine.event_handler = SingleRangedAttackHandler(
            self.engine,
            callback=lambda xy: actions.ItemAction(consumer, self.parent, xy),
        )
        return None

    def activate(self, action: actions.ItemAction) -> None:
        consumer = action.entity
        target = action.target_actor

        if not self.engine.game_map.visible[action.target_xy]:
            raise ImpossibleAction("You cannot target an area that you cannot see")
        if not target:
            raise ImpossibleAction("You must select an enemy to target")
        if target is consumer:
            raise ImpossibleAction("You cannot confuse yourself")

        self.engine.message_log.add_message(
            f"With a vacant and confused gaze the {target.name} starts to stumble around!",
            colors.status_effect_applied,
        )
        target.ai = components.ai.ConfusedEnemy(
            entity=target,
            previous_ai=target.ai,
            turns_remaining=self.number_of_turns,
        )
        self.consume()


class ReckoningConsumable(Consumable):
    def __init__(self, damage: int, radius: int):
        self.damage = damage
        self.radius = radius

    def get_action(self, consumer: Actor) -> Optional[actions.Action]:
        self.engine.message_log.add_message(
            "Select a target location", colors.needs_target
        )
        self.engine.event_handler = AreaRangedAttackHandler(
            self.engine,
            radius=self.radius,
            callback=lambda xy: actions.ItemAction(consumer, self.parent, xy),
        )
        return None

    def activate(self, action: actions.ItemAction) -> None:
        target_xy = action.target_xy

        if not self.engine.game_map.visible[target_xy]:
            raise ImpossibleAction("You cannot target an area that you cannot see")

        targets_hit = False
        for actor in self.engine.game_map.actors:
            if actor.distance(*target_xy) <= self.radius:
                self.engine.message_log.add_message(
                    f"The {actor.name} is hammered by the inevitable, taking {self.damage} damage!",
                    colors.light_orange,
                )
                actor.fighter.take_damage(self.damage)
                targets_hit = True

        if not targets_hit:
            raise ImpossibleAction("There are no targets in the radius")
        self.consume()


class HolyBlastConsumable(Consumable):
    def __init__(self, char: str, damage: int):
        self.char = char
        self.damage = damage

    def get_action(self, consumer: Actor) -> Optional[actions.Action]:
        self.engine.message_log.add_message(
            "Select a target location", colors.needs_target
        )
        self.engine.event_handler = CrossRangedAttackHandler(
            self.engine,
            char=self.char,
            callback=lambda xy: actions.ItemAction(consumer, self.parent, xy),
        )
        return None

    def activate(self, action: actions.ItemAction) -> None:
        target_x, target_y = action.target_xy

        if not self.engine.game_map.visible[target_x, target_y]:
            raise ImpossibleAction("You cannot target an area that you cannot see")

        player_hit = False
        enemy_hit = False
        for actor in self.engine.game_map.actors:
            # Basically draw the cross shape around the target and check if we're in it
            if (actor.x == target_x and target_y - 2 <= actor.y <= target_y + 3) or (
                actor.y == target_y and target_x - 2 <= actor.x <= target_x + 2
            ):
                if self.engine.player is actor:
                    player_hit = True
                else:
                    enemy_hit = True
                    self.engine.message_log.add_message(
                        f"The {actor.name} is purified by flame, taking {self.damage} damage!",
                        colors.light_orange,
                    )
                    actor.fighter.take_damage(self.damage)

        # Handle the player last to highlight the heals
        if player_hit:
            self.engine.message_log.add_message(
                f"The {self.engine.player.name} is purified by flame, recovering {self.damage//2} HP!",
                colors.hp_recovered,
            )
            self.engine.player.fighter.heal(self.damage // 2)

        if not player_hit and not enemy_hit:
            raise ImpossibleAction("There are no targets in the radius")
        self.consume()


class SunbeamConsumable(Consumable):
    def __init__(self, damage: int, maximum_range: int):
        self.damage = damage
        self.maximum_range = maximum_range

    def activate(self, action: actions.ItemAction) -> None:
        consumer = action.entity
        target = None
        closest_distance = self.maximum_range + 1.0

        for actor in self.engine.game_map.actors:
            if actor is not consumer and self.parent.game_map.visible[actor.x, actor.y]:
                distance = consumer.distance(actor.x, actor.y)

                if distance < closest_distance:
                    target = actor
                    closest_distance = distance

        if target:
            self.engine.message_log.add_message(
                f"Sunbeam blazes into {target.name}, glowing and pure, for {self.damage} damage!",
                colors.light_orange,
            )
            target.fighter.take_damage(self.damage)
            self.consume()
        else:
            raise ImpossibleAction("No enemy is close enough to strike")
