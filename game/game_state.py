import sys
import json
import math
import pygame
from . import player
import os.path
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

#from client import client_config
FRAME_RATE = 60
BLOCKS_PER_SEC = 20

FRAMES_PER_TICK = FRAME_RATE / BLOCKS_PER_SEC

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
    def __init__(self, players, maze, local_id, block_size):
        GameState.__init__(self, players, maze)
        self.local_player = local_id

        for id_, name in players:
            if id_ == local_id:
                self.players[id_] = player.LocalPlayer(id_, maze.starting_locations[id_], name)
            else:
                self.players[id_] = player.Player(id_, maze.starting_locations[id_], name)

            self.players[id_].px = maze.starting_locations[id_][0] * block_size
            self.players[id_].py = maze.starting_locations[id_][1] * block_size

        self.block_size = block_size
        self.radius = block_size / 2
        self.pixel_width = block_size * maze.width
        self.pixels_per_frame = block_size * FRAME_RATE / BLOCKS_PER_SEC
        self.walls = []
        for i in range(maze.width):
            for j in range(maze.width):
                if maze.maze[i * maze.width + j]:
                    self.walls.append(pygame.Rect(j * self.block_size, i * self.block_size, self.block_size, self.block_size))
        self.prio = 'x' 
    
    def tick(self):
        for p in self.players:
            if p.local:
                if p.illegal_move:
                    p.illegal_move = False
                    (p.px, p.py) = self.to_pixels(self.player.x, self.player.y)
                else:
                    self.handle_collision(p)
            else:
                (realX, realY) = self.to_pixels(self.player.x, self.player.y)
                p.px = p.px + (realX - p.px) / FRAMES_PER_TICK
                p.py = p.py + (realY - p.py) / FRAMES_PER_TICK

    def handle_collision(self, p):
        # New x, y
        new_x = p.px + self.pixels_per_frame * p.vel[0]
        new_y = p.py + self.pixels_per_frame * p.vel[1]

        # Check if new x,y is within the map
        if new_x < 0:
            new_x = 0
        elif new_x >= self.pixel_width - self.block_size:
            new_x = self.pixel_width - self.block_size
        if new_y < 0:
            new_y = 0
        elif new_y  > self.pixel_width - self.block_size:
            new_y = self.pixel_width - self.block_size

        def make_rect(x, y):
            return pygame.Rect(x, y,
                                self.block_size, self.block_size)

        bounding_rect = make_rect(new_x, new_y)

        wall = bounding_rect.collidelist(self.walls)
        if not wall == -1:
            if make_rect(p.px, new_y).collidelist(self.walls) == -1:
                new_x = self.round_pixel(p.px + self.radius)
            elif make_rect(new_x, p.py).collidelist(self.walls) == -1:
                new_y = self.round_pixel(p.py + self.radius)
            else:
                new_x, new_y = p.px, p.py

        p.px, p.py = new_x, new_y

        new_pos = self.to_coords((p.px + self.radius, p.py + self.radius))
        if new_pos[0] != p.x and new_pos[1] != p.y:
            # can't move in both x and y direction at the same time
            if self.prio == 'x':
                p.x = new_pos[0]
                self.prio = 'y'
            else:
                p.y = new_pos[1]
                self.prio = 'x'

        elif new_pos != (p.x, p.y):
            p.x, p.y = new_pos

    def to_pixels(self, x, y):
        return (
            math.floor(x * self.block_size),
            math.floor(y * self.block_size)
        )

    def round_pixel(self, pixel):
        return math.floor(pixel / self.block_size) * self.block_size

    def to_json(self):
        return json.dumps(self.players[self.local_player].serializable())

    def from_json(self, json_data):
        data = json.loads(json_data)
        self.winners = data['winners']

        for player in data['players']:
            n = player['id']
            x, y = self.players[n].x, self.players[n].y
            new_x, new_y = player['x'], player['y']

            if n == self.local_player:
                self.players[n].illegal_move = True
            else:
                self.players[n].vel = (new_x - x, new_y - y)

            self.players[n].x, self.players[n].y = new_x, new_y
