import json
from . import player

class Game_State:
    def __init__(self, player_amount, maze, local_player='-1'):
        self.maze = maze
        self.player_amount = player_amount
        self.players = []
        self.game_over = False
        self.winners = []
        self.illegal_movement = False
        self.local_player = local_player
        for i in range(player_amount):
            if i == local_player:
                self.players.append(player.LocalPlayer(i, maze.starting_locations[i]))
            else:
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

    def tick(self):
        for player in self.players:
            if self.legal_move(player.current_pos(), player.next_pos()):
                player.move()
            if player.x == self.maze.goal[0] and player.y == self.maze.goal[1]:
                self.game_over = True
                self.winners.append(player.player_number)

    # state_to_json is the inverse of from_json
    # Used by the server to send game state to clients
    def state_to_json(self, exclude=-1):
        player_jsons = []
        for player in self.players:
            if player.player_number == exclude:
                continue
            player_jsons.append(player.serializable())
        return json.dumps(dict([('winners', self.winners), ('players', player_jsons)]))

    def from_json(self, json_data):
        data = json.loads(json_data)
        self.winners = data['winners']

        for player in data['players']:
            n = player['player_number']
            if n == self.local_player:
                self.illegal_movement = True
            self.players[n].x = player['x']
            self.players[n].y = player['y']

    # client_to_json() packages the local player into json
    def client_to_json(self):
        return json.dumps(self.players[self.local_player].serializable())

    # client_from_json() is used by the server to update the position
    # of the client
    # Returns true if succesful
    # Returns false if move is illegal
    def client_from_json(self, json_data):
        data = json.loads(json_data)
        new_pos = (data['x'], data['y'])
        p = self.players[data['player_number']]

        if self.legal_move(p.current_pos(), new_pos):
            p.move_to(new_pos)
            if new_pos == self.maze.goal:
                self.winners.append(data['player_number'])
            return True
        return False
