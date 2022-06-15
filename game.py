class Game:
    def __init__(self, game_id, default_players):
        self.ready = False
        self.id = game_id
        self.players = default_players

    def connected(self):
        # Check if both players have connected
        return self.ready
