class Game:
    def __init__(self, game_id):
        self.ready = False
        self.id = game_id

    def connected(self):
        # Check if both players have connected
        return self.ready
