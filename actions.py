from __future__ import annotations

from typing import Optional, Tuple, TYPE_CHECKING

from constants import colors

if TYPE_CHECKING:
    from engine import Engine
    from entity import Actor, Entity


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


class EscapeAction(Action):
    def perform(self) -> bool:
        raise SystemExit()


class WaitAction(Action):
    def perform(self) -> bool:
        return True


class StairsUpAction(Action):
    def perform(self) -> bool:
        self.engine.message_log.add_message(
            "Sunlight and the village tempt you, but duty calls", fg=colors.welcome_text
        )
        return False


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
            return False  # No entity to attack

        damage = self.entity.fighter.power - target.fighter.defense
        attack_color = (
            colors.player_atk if self.entity is self.engine.player else colors.enemy_atk
        )
        attack_desc = f"{self.entity.name.capitalize()} attacks {target.name}"

        if damage > 0:
            self.engine.message_log.add_message(
                f"{attack_desc} for {damage} hit points", attack_color
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
            return False  # Destination is out of bounds
        if not self.engine.game_map.tiles["walkable"][dest_x, dest_y]:
            return False  # Destination is blocked by a tile
        if self.engine.game_map.get_blocking_entity_at_location(dest_x, dest_y):
            return False  # Destination is blocked by an entity

        self.entity.move(self.dx, self.dy)
        return True


class BumpAction(ActionWithDirection):
    def perform(self) -> None:
        if self.target_actor:
            return MeleeAction(self.entity, self.dx, self.dy).perform()
        else:
            match_entity = self.engine.game_map.get_entity_at_location(*self.dest_xy)

            # TODO Better way to detect "Stairs up", perhaps an Entity type, or new child class besides Actor
            if getattr(match_entity, "name", None) == "Stairs up":
                StairsUpAction(self.entity).perform()

            return MovementAction(self.entity, self.dx, self.dy).perform()
