from dataclasses import dataclass
from typing import Optional
import random

COLORS = ["🔴", "🔵", "⚫", "🟡"]
JOKER = "🃏"

@dataclass
class Tile:
    color: Optional[str]
    number: Optional[int]
    is_joker: bool = False

    def __str__(self):
        if self.is_joker:
            return JOKER
        return f"{self.color}{self.number}"

    def __eq__(self, other):
        if self.is_joker or other.is_joker:
            return True
        return self.color == other.color and self.number == other.number


def create_tile_set():
    tiles = []
    for color in COLORS:
        for number in range(1, 14):
            tiles.append(Tile(color, number))
            tiles.append(Tile(color, number))
    tiles.append(Tile(None, None, is_joker=True))
    tiles.append(Tile(None, None, is_joker=True))
    random.shuffle(tiles)
    return tiles
