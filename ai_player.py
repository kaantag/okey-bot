from player import Player
import random

class AIPlayer(Player):
    def __init__(self, user_id, name):
        super().__init__(user_id, name, is_bot=True)

    def choose_tile_to_discard(self):
        singles = self._find_singles()
        if singles:
            return max(singles, key=lambda t: t.number if not t.is_joker else 0)
        return random.choice(self.hand)

    def _find_singles(self):
        singles = []
        for tile in self.hand:
            if tile.is_joker:
                continue
            if not self._in_sequence(tile) and not self._in_set(tile):
                singles.append(tile)
        return singles

    def _in_sequence(self, tile):
        same_color = [t for t in self.hand if t.color == tile.color and not t.is_joker]
        numbers = sorted(set(t.number for t in same_color))
        for i, n in enumerate(numbers):
            if n == tile.number:
                if i > 0 and numbers[i-1] == n - 1:
                    return True
                if i < len(numbers)-1 and numbers[i+1] == n + 1:
                    return True
        return False

    def _in_set(self, tile):
        same_number = [t for t in self.hand if t.number == tile.number and not t.is_joker]
        return len(same_number) >= 2
