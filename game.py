from tile import Tile, create_tile_set
from player import Player
from ai_player import AIPlayer
import random

class OkeyGame:
    def __init__(self, chat_id):
        self.chat_id = chat_id
        self.players = []
        self.tiles = []
        self.discard_pile = []
        self.current_player_idx = 0
        self.joker_tile = None
        self.started = False
        self.waiting_discard = False

    def add_player(self, user_id, name):
        if len(self.players) >= 4:
            return False
        if any(p.user_id == user_id for p in self.players):
            return False
        self.players.append(Player(user_id, name))
        return True

    def fill_with_bots(self):
        bot_names = ["🤖 Bot Ali", "🤖 Bot Ayşe", "🤖 Bot Mehmet"]
        bot_id = -1
        while len(self.players) < 4:
            idx = len(self.players) - 1
            name = bot_names[idx] if idx < len(bot_names) else f"🤖 Bot {idx}"
            self.players.append(AIPlayer(bot_id, name))
            bot_id -= 1

    def start_game(self):
        self.tiles = create_tile_set()
        indicator = self.tiles.pop()
        if not indicator.is_joker:
            joker_num = (indicator.number % 13) + 1
            self.joker_tile = next(
                (t for t in self.tiles if t.color == indicator.color and t.number == joker_num),
                None
            )
        for i, player in enumerate(self.players):
            count = 15 if i == 0 else 14
            for _ in range(count):
                player.add_tile(self.tiles.pop())
        self.started = True
        self.waiting_discard = True

    def draw_tile(self, player):
        if not self.tiles:
            return None
        tile = self.tiles.pop()
        player.add_tile(tile)
        self.waiting_discard = True
        return tile

    def discard_tile(self, player, tile_index):
        if tile_index < 0 or tile_index >= len(player.hand):
            return None
        tile = player.hand.pop(tile_index)
        self.discard_pile.append(tile)
        self.waiting_discard = False
        return tile

    def take_from_discard(self, player):
        if not self.discard_pile:
            return None
        tile = self.discard_pile.pop()
        player.add_tile(tile)
        self.waiting_discard = True
        return tile

    @property
    def current_player(self):
        return self.players[self.current_player_idx]

    def next_turn(self):
        self.current_player_idx = (self.current_player_idx + 1) % len(self.players)
        self.waiting_discard = False

    def calculate_scores(self):
        return {p.name: p.hand_value() for p in self.players}
