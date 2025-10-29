from __future__ import annotations

import os
from typing import Callable, Optional, Tuple, TYPE_CHECKING, Union

import tcod.constants
import tcod.event
from tcod import libtcodpy

import actions
from actions import Action, BumpAction, EscapeAction, PickupAction, WaitAction
from constants import colors, general
from exceptions import QuitWithoutSaving

if TYPE_CHECKING:
    from engine import Engine
    from entity import Item

MOVE_KEYS = {
    # WSAD
    tcod.event.KeySym.W: (0, -1),
    tcod.event.KeySym.S: (0, 1),
    tcod.event.KeySym.A: (-1, 0),
    tcod.event.KeySym.D: (1, 0),
    # Arrow keys
    tcod.event.KeySym.UP: (0, -1),
    tcod.event.KeySym.DOWN: (0, 1),
    tcod.event.KeySym.LEFT: (-1, 0),
    tcod.event.KeySym.RIGHT: (1, 0),
    tcod.event.KeySym.HOME: (-1, -1),
    tcod.event.KeySym.END: (-1, 1),
    tcod.event.KeySym.PAGEUP: (1, -1),
    tcod.event.KeySym.PAGEDOWN: (1, 1),
    # Numpad keys
    tcod.event.KeySym.KP_1: (-1, 1),
    tcod.event.KeySym.KP_2: (0, 1),
    tcod.event.KeySym.KP_3: (1, 1),
    tcod.event.KeySym.KP_4: (-1, 0),
    tcod.event.KeySym.KP_6: (1, 0),
    tcod.event.KeySym.KP_7: (-1, -1),
    tcod.event.KeySym.KP_8: (0, -1),
    tcod.event.KeySym.KP_9: (1, -1),
}

CURSOR_Y_KEYS = {
    tcod.event.KeySym.UP: -1,
    tcod.event.KeySym.DOWN: 1,
    tcod.event.KeySym.PAGEUP: -10,
    tcod.event.KeySym.PAGEDOWN: 10,
}

WAIT_KEYS = {
    tcod.event.KeySym.KP_5,
    tcod.event.KeySym.CLEAR,
}

CONFIRM_KEYS = {
    tcod.event.KeySym.RETURN,
    tcod.event.KeySym.KP_ENTER,
}

ESCAPE_KEYS = {tcod.event.KeySym.ESCAPE}

ActionOrHandler = Union[Action, "BaseEventHandler"]
"""An event handler return value which can trigger an action or switch active handlers

If a handler is returned then it will become the active handler for future events
If an action is returned it will be attempted and if it's valid then
MainGameEventHandler will become the active handler
"""


class BaseEventHandler(tcod.event.EventDispatch[ActionOrHandler]):
    def handle_event(self, event: tcod.event.Event) -> BaseEventHandler:
        """Handle an event and return the next active event handler"""
        state = self.dispatch(event)
        if isinstance(state, BaseEventHandler):
            return state
        assert not isinstance(state, Action), f"{self!r} can not handle actions."
        return self

    def on_render(
        self, console: tcod.console.Console, context: tcod.context.Context
    ) -> None:
        raise NotImplementedError()

    def ev_quit(self, event: tcod.event.Quit) -> Optional[Action]:
        raise SystemExit()


class EventHandler(BaseEventHandler):
    def __init__(self, engine: Engine):
        self.engine = engine

    def handle_event(self, event: tcod.event.Event) -> BaseEventHandler:
        """Handle events for input handlers with an engine"""
        action_or_state = self.dispatch(event)
        if isinstance(action_or_state, BaseEventHandler):
            return action_or_state
        if self.handle_action(action_or_state):
            # A valid action was performed
            if not self.engine.player.is_alive:
                # The player was killed sometime during or after the action
                return GameOverEventHandler(self.engine)
            return MainGameEventHandler(self.engine)  # Return to the main handler
        return self

    # TODO Already had a solution for skipping enemy turns, so ignored the section after adding the "Impossible" exception from https://rogueliketutorials.com/tutorials/tcod/v2/part-8/
    def handle_action(self, action: Optional[Action]) -> bool:
        if action and action.perform():
            self.engine.handle_enemy_turns()
            self.engine.update_fov()  # Update the FOV before the players next action
            return True
        return False

    def ev_mousemotion(self, event: tcod.event.MouseMotion) -> None:
        x, y = event.position

        if self.engine.game_map.in_bounds(x, y):
            self.engine.mouse_location = (int(x), int(y))

    def on_render(
        self, console: tcod.console.Console, context: tcod.context.Context
    ) -> None:
        self.engine.render(console, context)


class MainGameEventHandler(EventHandler):
    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[ActionOrHandler]:
        action: Optional[Action] = None
        player = self.engine.player

        # Key binding configuration
        key = event.sym
        if key in MOVE_KEYS:
            dx, dy = MOVE_KEYS[key]
            action = BumpAction(player, dx, dy)
        elif key in WAIT_KEYS:
            action = WaitAction(player)
        elif key in ESCAPE_KEYS:
            action = EscapeAction(player)
        # TODO Perform StairsUpAction once we have a multi-level dungeon
        # elif key == tcod.event.KeySym.PERIOD and event.mod & tcod.event.Modifier.SHIFT:
        #     action = StairsUpAction(player)
        elif key == tcod.event.KeySym.G:
            action = PickupAction(player)
        elif key == tcod.event.KeySym.I:
            return InventoryActivateHandler(self.engine)
        elif key == tcod.event.KeySym.P:  # P for Put Down
            return InventoryDropHandler(self.engine)
        elif key == tcod.event.KeySym.SLASH:
            return LookHandler(self.engine)
        elif key == tcod.event.KeySym.V:
            return HistoryViewer(self.engine)

        return action


class GameOverEventHandler(EventHandler):
    def on_quit(self) -> None:
        """Handle exiting out of a finished game"""
        if os.path.exists(general.SAVE_FILE):
            os.remove(general.SAVE_FILE)  # Deletes the active save file
        raise QuitWithoutSaving()  # Avoid saving a finished game

    def ev_quit(self, event: tcod.event.Quit) -> None:
        self.on_quit()

    def ev_keydown(self, event: tcod.event.KeyDown) -> None:
        if event.sym in ESCAPE_KEYS:
            self.on_quit()


class PopupMessage(BaseEventHandler):
    """Display a popup text window"""

    def __init__(self, parent_handler: BaseEventHandler, text: str):
        self.parent = parent_handler
        self.text = text

    def on_render(
        self, console: tcod.console.Console, context: tcod.context.Context
    ) -> None:
        """Render the parent and dim the result, then print the message on top"""
        self.parent.on_render(console, context)
        console.rgb["fg"] //= 10
        console.rgb["bg"] //= 10

        console.print(
            console.width // 2,
            console.height // 2,
            self.text,
            fg=colors.white,
            bg=colors.black,
            alignment=libtcodpy.CENTER,
        )

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[BaseEventHandler]:
        """Any key returns to the parent handler"""
        return self.parent


class AskUserEventHandler(EventHandler):
    """Handles user input for actions which require special input"""

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[ActionOrHandler]:
        """By default any key exits this input handler"""
        if event.sym in {  # Ignore modifier keys
            tcod.event.KeySym.LSHIFT,
            tcod.event.KeySym.RSHIFT,
            tcod.event.KeySym.LCTRL,
            tcod.event.KeySym.RCTRL,
            tcod.event.KeySym.LALT,
            tcod.event.KeySym.RALT,
        }:
            return None
        return self.on_exit()

    def ev_mousebuttondown(
        self, event: tcod.event.MouseButtonDown
    ) -> Optional[ActionOrHandler]:
        """By default any mouse click exits this input handler"""
        return self.on_exit()

    def on_exit(self) -> Optional[ActionOrHandler]:
        """Called when the user is trying to exit or cancel an action

        By default this returns to the main event handler
        """
        return MainGameEventHandler(self.engine)


class InventoryEventHandler(AskUserEventHandler):
    """This handler lets the user select an item

    What happens then depends on the subclass
    """

    TITLE = "<missing title>"

    def on_render(
        self, console: tcod.console.Console, context: tcod.context.Context
    ) -> None:
        """Render an inventory menu, which displays the items in the inventory, and the letter to select them
        Will move to a different position based on where the player is located, so the player can always see where they are
        """
        super().on_render(console, context)
        number_of_items_in_inventory = len(self.engine.player.inventory.items)

        height = number_of_items_in_inventory + 2

        if height <= 3:
            height = 3

        if self.engine.player.x <= 30:
            x = 40
        else:
            x = 0

        y = 0

        width = len(self.TITLE) + 4

        console.draw_frame(
            x=x,
            y=y,
            width=width,
            height=height,
            title=self.TITLE,
            clear=True,
            fg=(255, 255, 255),
            bg=(0, 0, 0),
        )

        self.engine.player.inventory.items.sort(key=lambda item: item.name)

        if number_of_items_in_inventory > 0:
            for i, item in enumerate(self.engine.player.inventory.items):
                item_key = chr(ord("a") + i)
                console.print(x + 1, y + i + 1, f"({item_key}) {item.name}")
        else:
            console.print(x + 1, y + 1, "(Empty)")

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[ActionOrHandler]:
        player = self.engine.player
        key = event.sym
        index = key - tcod.event.KeySym.A

        if 0 <= index <= 26:
            try:
                selected_item = player.inventory.items[index]
            except IndexError:
                self.engine.message_log.add_message("Invalid entry", colors.invalid)
                return None
            return self.on_item_selected(selected_item)
        return super().ev_keydown(event)

    def on_item_selected(self, item: Item) -> Optional[ActionOrHandler]:
        """Called when the user selects a valid item"""
        raise NotImplementedError()


class InventoryActivateHandler(InventoryEventHandler):
    """Handle using an inventory item"""

    TITLE = "Select an item to use"

    def on_item_selected(self, item: Item) -> Optional[ActionOrHandler]:
        """Return the action for the selected item"""
        return item.consumable.get_action(self.engine.player)


class InventoryDropHandler(InventoryEventHandler):
    """Handle dropping an inventory item"""

    TITLE = "Select an item to put down"

    def on_item_selected(self, item: Item) -> Optional[ActionOrHandler]:
        """Drop this item"""
        return actions.DropItem(self.engine.player, item)


class SelectIndexHandler(AskUserEventHandler):
    """Handles asking the user for an index on the map"""

    def __init__(self, engine: Engine):
        """Sets the cursor to the player when this handler is constructed"""
        super().__init__(engine)
        player = self.engine.player
        engine.mouse_location = player.x, player.y

    def on_render(
        self, console: tcod.console.Console, context: tcod.context.Context
    ) -> None:
        """Highlight the tile under the cursor"""
        super().on_render(console, context)
        x, y = self.engine.mouse_location
        console.rgb["bg"][x, y] = colors.white
        console.rgb["fg"][x, y] = colors.black

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[ActionOrHandler]:
        """Check for key movement or confirmation keys."""
        key = event.sym
        if key in MOVE_KEYS:
            modifier = 1  # Holding modifier keys will speed up key movement
            if event.mod & (tcod.event.Modifier.LSHIFT | tcod.event.Modifier.RSHIFT):
                modifier *= 5
            if event.mod & (tcod.event.Modifier.LCTRL | tcod.event.Modifier.RCTRL):
                modifier *= 10
            if event.mod & (tcod.event.Modifier.LALT | tcod.event.Modifier.RALT):
                modifier *= 20

            x, y = self.engine.mouse_location
            dx, dy = MOVE_KEYS[key]
            x += dx * modifier
            y += dy * modifier
            # Clamp the cursor index to the map size
            x = max(0, min(x, self.engine.game_map.width - 1))
            y = max(0, min(y, self.engine.game_map.height - 1))
            self.engine.mouse_location = x, y
            return None
        elif key in CONFIRM_KEYS:
            return self.on_index_selected(*self.engine.mouse_location)
        return super().ev_keydown(event)

    def ev_mousebuttondown(
        self, event: tcod.event.MouseButtonDown
    ) -> Optional[ActionOrHandler]:
        """Left click confirms a selection"""
        if self.engine.game_map.in_bounds(*event.tile):
            if event.button == 1:
                return self.on_index_selected(*event.tile)
        return super().ev_mousebuttondown(event)

    def on_index_selected(self, x: int, y: int) -> Optional[ActionOrHandler]:
        """Called when an index is selected"""
        raise NotImplementedError()


class SingleRangedAttackHandler(SelectIndexHandler):
    """Handles targeting a single enemy. Only the enemy selected will be affected"""

    def __init__(
        self, engine: Engine, callback: Callable[[Tuple[int, int]], Optional[Action]]
    ):
        super().__init__(engine)

        self.callback = callback

    def on_index_selected(self, x: int, y: int) -> Optional[Action]:
        """Return to main handler"""
        self.engine.event_handler = MainGameEventHandler(self.engine)
        return self.callback((x, y))


class CrossRangedAttackHandler(SelectIndexHandler):
    """Handles targeting a cross shape. Any entity within the area will be affected"""

    def __init__(
        self,
        engine: Engine,
        char: str,
        callback: Callable[[Tuple[int, int]], Optional[Action]],
    ):
        super().__init__(engine)

        self.char = char
        self.callback = callback

    def on_render(
        self, console: tcod.console.Console, context: tcod.context.Context
    ) -> None:
        """Highlight the tile under the cursor"""
        super().on_render(console, context)
        x, y = self.engine.mouse_location

        # Convert our requested Unicode character to the int equivalent for use with our draw
        unicode_char_int = ord(self.char)
        console.draw_rect(  # Left cross
            x=x - 2,
            y=y,
            width=2,
            height=1,
            fg=colors.red,
            bg=colors.yellow,
            ch=unicode_char_int,
        )
        console.draw_rect(  # Right cross
            x=x + 1,
            y=y,
            width=2,
            height=1,
            fg=colors.red,
            bg=colors.yellow,
            ch=unicode_char_int,
        )
        console.draw_rect(  # Top cross
            x=x,
            y=y - 2,
            width=1,
            height=2,
            fg=colors.red,
            bg=colors.yellow,
            ch=unicode_char_int,
        )
        console.draw_rect(  # Bottom cross
            x=x,
            y=y + 1,
            width=1,
            height=4,
            fg=colors.red,
            bg=colors.yellow,
            ch=unicode_char_int,
        )

    def on_index_selected(self, x: int, y: int) -> Optional[Action]:
        """Return to main handler"""
        self.engine.event_handler = MainGameEventHandler(self.engine)
        return self.callback((x, y))


class AreaRangedAttackHandler(SelectIndexHandler):
    """Handles targeting an area within a given radius. Any entity within the area will be affected"""

    def __init__(
        self,
        engine: Engine,
        radius: int,
        callback: Callable[[Tuple[int, int]], Optional[Action]],
    ):
        super().__init__(engine)

        self.radius = radius
        self.callback = callback

    def on_render(
        self, console: tcod.console.Console, context: tcod.context.Context
    ) -> None:
        """Highlight the tile under the cursor"""
        super().on_render(console, context)
        x, y = self.engine.mouse_location

        # Draw a square around the targeted area, so the player can see the affected tiles
        console.draw_frame(
            x=x - self.radius - 1,
            y=y - self.radius - 1,
            width=self.radius**2,
            height=self.radius**2,
            fg=colors.red,
            clear=False,
        )

    def on_index_selected(self, x: int, y: int) -> Optional[Action]:
        """Return to main handler"""
        self.engine.event_handler = MainGameEventHandler(self.engine)
        return self.callback((x, y))


class LookHandler(SelectIndexHandler):
    """Lets the player look around using the keyboard"""

    def on_index_selected(self, x: int, y: int) -> MainGameEventHandler:
        """Return to main handler"""
        return MainGameEventHandler(self.engine)


class HistoryViewer(EventHandler):
    """Print the history on a larger window which can be navigated"""

    def __init__(self, engine: Engine):
        super().__init__(engine)
        self.log_length = len(engine.message_log.messages)
        self.cursor = self.log_length - 1

    def on_render(
        self, console: tcod.console.Console, context: tcod.context.Context
    ) -> None:
        super().on_render(console, context)
        log_console = tcod.console.Console(console.width, console.height)

        # Draw a frame with a custom banner title
        log_console.draw_frame(0, 0, log_console.width, log_console.height)
        log_console.print_box(
            0,
            0,
            log_console.width,
            1,
            "┤ Message History (press any key to close) ├",
            alignment=tcod.constants.CENTER,
        )

        # Render the message log using the cursor parameter
        self.engine.message_log.render_messages(
            log_console,
            1,
            1,
            log_console.width,
            log_console.height - 2,
            self.engine.message_log.messages[: self.cursor + 1],
        )
        log_console.blit(console, 0, 0)

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[MainGameEventHandler]:
        # Fancy conditional movement to make it feel right
        if event.sym in CURSOR_Y_KEYS:
            adjust = CURSOR_Y_KEYS[event.sym]
            if adjust < 0 and self.cursor == 0:
                # Only move from the top to the bottom when you're on the edge
                self.cursor = self.log_length - 1
            elif adjust > 0 and self.cursor == self.log_length - 1:
                # Same with bottom to top movement
                self.cursor = 0
            else:
                # Otherwise move while staying clamped to the bounds of the history log
                self.cursor = max(0, min(self.cursor + adjust, self.log_length - 1))
        elif event.sym == tcod.event.KeySym.HOME:
            self.cursor = 0  # Move directly to the top message
        elif event.sym == tcod.event.KeySym.END:
            self.cursor = self.log_length - 1  # Move directly to the last message
        else:  # Any other key moves back to the main game state
            return MainGameEventHandler(self.engine)
        return None
