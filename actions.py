from __future__ import annotations

from typing import Optional, Tuple, TYPE_CHECKING

import exceptions
from constants import colors

if TYPE_CHECKING:
    from engine import Engine
    from entity import Actor, Entity, Item


class Action:
    def __init__(self, entity: Actor) -> None:
        super().__init__()
        self.entity = entity

    @property
    def engine(self) -> Engine:
        """Return the engine this action belongs to"""
        return self.entity.game_map.engine

    def perform(self) -> bool:
        """Perform this action with the objects needed to determine its scope

        `self.engine` is the scope this action is being performed in

        `self.entity` is the object performing the action

        This method must be overridden by Action subclasses
        """
        raise NotImplementedError()


class PickupAction(Action):
    """Pickup an item and add it to the inventory, if there is room for it"""

    def __init__(self, entity: Actor):
        super().__init__(entity)

    def perform(self) -> None:
        actor_location_x = self.entity.x
        actor_location_y = self.entity.y
        inventory = self.entity.inventory

        if not inventory:
            return

        for item in self.engine.game_map.items:
            if actor_location_x == item.x and actor_location_y == item.y:
                if len(inventory.items) >= inventory.capacity:
                    raise exceptions.ImpossibleAction("Your inventory is full")

                self.engine.game_map.entities.remove(item)
                item.parent = self.entity.inventory
                inventory.items.append(item)

                self.engine.message_log.add_message(f"You picked up the {item.name}!")
                return

        raise exceptions.ImpossibleAction("There is nothing here to pick up")


class ItemAction(Action):
    def __init__(
        self, entity: Actor, item: Item, target_xy: Optional[Tuple[int, int]] = None
    ):
        super().__init__(entity)
        self.item = item
        if not target_xy:
            target_xy = entity.x, entity.y
        self.target_xy = target_xy

    @property
    def target_actor(self) -> Optional[Actor]:
        """Return the actor at this actions destination"""
        return self.engine.game_map.get_actor_at_location(*self.target_xy)

    def perform(self) -> bool:
        """Invoke the items ability, this action will be given to provide context"""
        if self.item.consumable:
            self.item.consumable.activate(self)
        return False


class EscapeAction(Action):
    def perform(self) -> bool:
        raise SystemExit()


class DropItem(ItemAction):
    def perform(self) -> None:
        if self.entity.equipment.item_is_equipped(self.item):
            self.entity.equipment.toggle_equip(self.item)

        self.entity.inventory.drop(self.item)


class EquipAction(Action):
    def __init__(self, entity: Actor, item: Item):
        super().__init__(entity)

        self.item = item

    def perform(self) -> None:
        self.entity.equipment.toggle_equip(self.item)


class WaitAction(Action):
    def perform(self) -> bool:
        return True


class StairsUpAction(Action):
    def perform(self) -> bool:
        self.engine.message_log.add_message(
            "Sunlight and the village tempt you, but duty calls", fg=colors.welcome_text
        )
        return False


class TakeStairsAction(Action):
    def perform(self) -> None:
        """
        Take the stairs, if any exist at the entity's location
        """
        if (self.entity.x, self.entity.y) == self.engine.game_map.downstairs_location:
            self.engine.game_world.generate_floor()
            self.engine.message_log.add_message(
                "You descend the creaky staircase", colors.welcome_text
            )
        # TTODO Stairs up done here
        else:
            raise exceptions.ImpossibleAction("There are no stairs here")


class ActionWithDirection(Action):
    def __init__(self, entity: Actor, dx: int, dy: int):
        super().__init__(entity)
        self.dx = dx
        self.dy = dy

    @property
    def dest_xy(self) -> Tuple[int, int]:
        """Returns this actions destination"""
        return self.entity.x + self.dx, self.entity.y + self.dy

    @property
    def blocking_entity(self) -> Optional[Entity]:
        """Return the blocking entity at this actions destination"""
        return self.engine.game_map.get_blocking_entity_at_location(*self.dest_xy)

    @property
    def target_actor(self) -> Optional[Actor]:
        """Return the actor at this actions destination"""
        return self.engine.game_map.get_actor_at_location(*self.dest_xy)

    def perform(self) -> bool:
        raise NotImplementedError()


class MeleeAction(ActionWithDirection):
    def perform(self) -> bool:
        target = self.target_actor
        if not target:
            raise exceptions.ImpossibleAction("Nothing to attack")

        damage = self.entity.fighter.base_power - target.fighter.base_defense
        attack_color = (
            colors.player_atk if self.entity is self.engine.player else colors.enemy_atk
        )
        attack_desc = f"{self.entity.name.capitalize()} attacks {target.name}"

        if damage > 0:
            self.engine.message_log.add_message(
                f"{attack_desc} for {damage} damage", attack_color
            )
            target.fighter.hp -= damage
        else:
            self.engine.message_log.add_message(
                f"{attack_desc} but does no damage", attack_color
            )
        return True


class MovementAction(ActionWithDirection):
    # Example from tcod docs on diagonal movement: https://python-tcod.readthedocs.io/en/latest/tcod/event.html#tcod.event.get_keyboard_state
    # x = int(state[tcod.event.Scancode.D]) - int(state[tcod.event.Scancode.A])
    # y = int(state[tcod.event.Scancode.S]) - int(state[tcod.event.Scancode.W])
    # print(f"X AND Y on movement {x} and {y}")

    def perform(self) -> bool:
        dest_x, dest_y = self.dest_xy

        if not self.engine.game_map.in_bounds(dest_x, dest_y):
            raise exceptions.ImpossibleAction("That way is blocked")
        if not self.engine.game_map.tiles["walkable"][dest_x, dest_y]:
            raise exceptions.ImpossibleAction("That way is blocked")
        if self.engine.game_map.get_blocking_entity_at_location(dest_x, dest_y):
            raise exceptions.ImpossibleAction("That way is blocked")

        self.entity.move(self.dx, self.dy)
        return True


class BumpAction(ActionWithDirection):
    def perform(self) -> bool:
        if self.target_actor:
            return MeleeAction(self.entity, self.dx, self.dy).perform()
        else:
            match_entity = self.engine.game_map.get_entity_at_location(*self.dest_xy)

            # TODO Better way to detect "Stairs up", perhaps an Entity type, or new child class besides Actor
            if getattr(match_entity, "name", None) == "Stairs up":
                StairsUpAction(self.entity).perform()

            return MovementAction(self.entity, self.dx, self.dy).perform()
