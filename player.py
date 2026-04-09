from tile import Tile

class Player:
    def __init__(self, user_id, name, is_bot=False):
        self.user_id = user_id
        self.name = name
        self.is_bot = is_bot
        self.hand = []
        self.score = 0

    def add_tile(self, tile):
        self.hand.append(tile)

    def remove_tile(self, tile):
        for t in self.hand:
            if t == tile:
                self.hand.remove(t)
                return True
        return False

    def hand_value(self):
        total = 0
        for tile in self.hand:
            if tile.is_joker:
                total += 30
            else:
                total += tile.number
        return total

    def hand_str(self):
        return " ".join(str(t) for t in self.hand)
