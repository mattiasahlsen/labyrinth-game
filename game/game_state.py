import json
from . import player

class Game_State:
    def __init__(self, player_amount, maze):
        self.maze = maze
        self.player_amount = player_amount
        self.players = []
        self.game_over = False
        self.winners = []
        for i in range(player_amount):
            self.players.append(player.Player(i, maze.starting_locations[i]))

    def set_vel(self, player_number, direction):
        self.players[player_number].vel = direction

    def legal_move(self, next_pos):
        x = next_pos[0]
        y = next_pos[1]
        # Out of bounds
        if x < 0 or x >= self.maze.width or y < 0 or y >= self.maze.width:
            return False
        # Maze wall
        if self.maze.maze[y * self.maze.width + x]:
            return False
        return True

    def tick(self):
        for player in self.players:
            if self.legal_move(player.next_pos()):
                player.move()
            if player.x == self.maze.goal[0] and player.y == self.maze.goal[1]:
                self.game_over = True
                self.winners.append(player.player_number)
            player.vel = (0, 0)

    def state_to_json(self):
        player_jsons = []
        for player in self.players:
            player_jsons.append(player.serializable())
        return json.dumps(dict([('winners', self.winners), ('players', player_jsons)]))

    def from_json(self, json_data):
        data = json.loads(json_data)
        self.winners = data['winners']

        for player in data['players']:
            n = player['player_number']

            self.players[n].x = player['x']
            self.players[n].y = player['y']
