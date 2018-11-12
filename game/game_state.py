import json
import math
from . import player

class GameState:
    def __init__(self, id_name_pairs, maze):
        self.maze = maze
        self.player_amount = len(id_name_pairs)
        self.players = []
        self.winners = []
        for id_, name in id_name_pairs:
            self.players.append(player.Player(id_, maze.starting_locations[id_], name))

    def set_vel(self, player_number, direction):
        self.players[player_number].vel = direction

    def legal_move(self, old_pos, next_pos):
        x = next_pos[0]
        y = next_pos[1]
        if not (isinstance(x, int) and isinstance(y, int)):
            return False
        if abs(x - old_pos[0]) + abs(y - old_pos[1]) > 1:
            return False
        # Out of bounds
        if x < 0 or x >= self.maze.width or y < 0 or y >= self.maze.width:
            return False
        # Maze wall
        if self.maze.maze[y * self.maze.width + x]:
            return False
        return True

    def to_json(self, exclude=-1):
        player_jsons = []
        for player in self.players:
            if player.id == exclude:
                continue
            player_jsons.append(player.serializable())
        return json.dumps(dict([('winners', self.winners), ('players', player_jsons)]))

    def from_json(self, json_data):
        data = json.loads(json_data)
        new_pos = (data['x'], data['y'])
        p = self.players[data['id']]

        if self.legal_move(p.current_pos(), new_pos):
            p.move_to(new_pos)
            (gx, gy), (x, y) = self.maze.goal, new_pos
            dx, dy = gx - x, gy - y
            if dx <= 1 and dx >= 0 and dy <= 1 and dy >= 0:
                self.winners.append(data['id'])
            return True
        return False

class LocalGameState(GameState):
    def __init__(self, players, maze, local_id):
        GameState.__init__(self, players, maze)
        self.local_player = local_id
        self.players[local_id] = player.LocalPlayer(local_id, maze.starting_locations[local_id], self.players[local_id].name)

    def to_json(self):
        return json.dumps(self.players[self.local_player].serializable())

    def from_json(self, json_data):
        data = json.loads(json_data)
        self.winners = data['winners']

        for player in data['players']:
            n = player['id']
            if n == self.local_player:
                self.players[n].illegal_move = True
            self.players[n].x = player['x']
            self.players[n].y = player['y']
