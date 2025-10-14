from typing import Tuple

class Entity:
    """
    A generic object to represent players, enemies, items, etc.
    """
    def __init__(self, x: int, y: int, char: str, color: Tuple[int, int, int], light_radius=8):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.light_radius = light_radius

    def move(self, dx: int, dy: int) -> None:
        # Move the entity by the given amount
        self.x += dx
        self.y += dy