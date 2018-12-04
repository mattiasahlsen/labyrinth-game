import sys
import json
import math
import pygame
from . import player
import os.path
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))


class GameState:
    def __init__(self, maze, players=None):
        self.players = {}
        if players:
            for player in players:
                self.players[player.id] = player
        self.maze = maze
        self.winners = []

    def add_player(self, player):
        self.players[player.id] = player

    def add_players(self, players):
        for player in players:
            self.players[player.id] = player

    def set_vel(self, player_number, direction):
        self.players[player_number].vel = direction

    def legal_move(self, pos, next_pos):
        x = next_pos[0]
        y = next_pos[1]
        # can't move more than 1 step at a time on one axis
        if abs(next_pos[0] - pos[0]) > 1 or abs(next_pos[1] - pos[1]) > 1:
            return False
        if not (isinstance(x, int) and isinstance(y, int)):
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
        for _, player in self.players.items():
            if player.id == exclude:
                continue
            player_jsons.append(player.serializable())
        return json.dumps(dict([('winners', self.winners), ('players', player_jsons)]))
    
    def to_json_name(self):
        player_jsons = []
        for _, player in self.players.items():
            dict_of_player = player.serializable()
            dict_of_player['name'] = player.name
            player_jsons.append(dict_of_player)
        return json.dumps(dict([('winners', self.winners), ('players', player_jsons)]))
    
    def from_json(self, json_data):
        data = json.loads(json_data)
        new_pos = (data['x'], data['y'])
        p = self.players[data['id']]

        if self.legal_move((p.x, p.y), new_pos):
            p.move_to(new_pos)
            (gx, gy), (x, y) = self.maze.goal, new_pos
            dx, dy = gx - x, gy - y
            if dx <= 1 and dx >= 0 and dy <= 1 and dy >= 0:
                if data['id'] not in self.winners:
                    self.winners.append(data['id'])
            return True
        return False
    def get_players(self):
        return self.players
    def set_players(self, players):
        self.players = players
    def get_player(self, mId):
        return self.players[mId]

    
