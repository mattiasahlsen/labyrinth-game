import json
from . import player

class GameState:
    def __init__(self, player_amount, maze):
        self.maze = maze
        self.player_amount = player_amount
        self.players = []
        self.winners = []
        for i in range(player_amount):
            self.players.append(player.Player(i, maze.starting_locations[i]))

    def set_vel(self, player_number, direction):
        self.players[player_number].vel = direction

    def legal_move(self, old_pos, next_pos):
        x = next_pos[0]
        y = next_pos[1]
        if abs(x - old_pos[0]) + abs(y - old_pos[1]) > 2:
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
            if new_pos == self.maze.goal:
                self.winners.append(data['id'])
            return True
        return False

class LocalGameState(GameState):
    def __init__(self, player_amount, maze, local_player_id):
        self.maze = maze
        self.player_amount = player_amount
        self.players = []
        self.winners = []
        self.local_player = local_player_id
        for i in range(player_amount):
            if (i == local_player_id):
                self.players.append(player.LocalPlayer(i, maze.starting_locations[i]))
            else:
                self.players.append(player.Player(i, maze.starting_locations[i]))
    
    # client_to_json() packages the local player into json
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