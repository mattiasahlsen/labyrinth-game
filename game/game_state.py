from . import maze
from . import player
import json

class Game_State:
    def __init__(self, player_amount, maze):
        self.maze = maze
        self.player_amount = player_amount
        self.players = []
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
            player.vel = (0, 0)

    def state_as_json(self):
        data = []
        for player in self.players:
            data.append(player.toJSON())
        return(json.dumps(data))

    def from_json(self, json_data):
        data = json.loads(json_data)
        for json_player in data:
            player = json.loads(json_player)
            n = player['player_number']
            
            self.players[n].x = player['x']
            self.players[n].y = player['y']