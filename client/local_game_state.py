import json
import math
import pygame
from game import game_state, player
import client_config

from client_config import BLOCKS_PER_SEC


class LocalGameState(game_state.GameState):
    def __init__(self, maze, players, local_id, block_size):
        print(str(local_id))
        game_state.GameState.__init__(self, maze, players)
        self.block_size = block_size
        self.radius = block_size / 2
        self.pixel_width = block_size * maze.width

        for player in players:
            if player.id == local_id:
                self.local_player = player
            player.px, player.py = self.to_pixels(player.x, player.y)

        self.walls = []
        for i in range(maze.width):
            for j in range(maze.width):
                if maze.maze[i * maze.width + j]:
                    self.walls.append(pygame.Rect(j * self.block_size, i * self.block_size, self.block_size, self.block_size))

    def tick(self, fps):
        if fps == 0:
            fps = 1 # no division by 0

        pixels_per_frame = self.block_size * BLOCKS_PER_SEC / fps
        frames_per_tick = fps / BLOCKS_PER_SEC
        for _, p in self.players.items():
            if p.local:
                if p.illegal_move:
                    p.illegal_move = False
                    (p.px, p.py) = self.to_pixels(p.x, p.y)
                else:
                    new_px = p.px + pixels_per_frame * p.vel[0]
                    new_py = p.py + pixels_per_frame * p.vel[1]
                    self.handle_collision(p, new_px, new_py)
            else:
                (real_x, real_y) = self.to_pixels(p.x, p.y)
                p.px = p.px + (real_x - p.px) / frames_per_tick
                p.py = p.py + (real_y - p.py) / frames_per_tick

    def handle_collision(self, p, new_px, new_py):
        # Check if new x,y is within the map
        if new_px < 0:
            new_px = 0
        elif new_px >= self.pixel_width - self.block_size:
            new_px = self.pixel_width - self.block_size
        if new_py < 0:
            new_py = 0
        elif new_py  > self.pixel_width - self.block_size:
            new_py = self.pixel_width - self.block_size

        def make_rect(x, y):
            return pygame.Rect(x, y, self.block_size, self.block_size)

        bounding_rect = make_rect(round(new_px), round(new_py))

        wall = bounding_rect.collidelist(self.walls)
        if not wall == -1:
            if make_rect(p.px, new_py).collidelist(self.walls) == -1:
                new_px = self.round_pixel(p.px + self.radius)
            elif make_rect(new_px, p.py).collidelist(self.walls) == -1:
                new_py = self.round_pixel(p.py + self.radius)
            else:
                new_py = self.round_pixel(p.py + self.radius)
                new_px = self.round_pixel(p.px + self.radius)

        p.px, p.py = new_px, new_py
        p.x, p.y = self.to_coords(p.px + self.radius, p.py + self.radius)

    def round_pixel(self, pixel):
        return math.floor(pixel / self.block_size) * self.block_size

    def to_json(self):
        return json.dumps(self.local_player.serializable())

    def from_json(self, json_data):
        data = json.loads(json_data)
        self.winners = data['winners']
        for player in data['players']:
            print(str(player['id']))
        for player in data['players']:
            n = player['id']
            x, y = self.players[n].x, self.players[n].y
            new_px, new_py = player['x'], player['y']

            if n == self.local_player.id:
                self.players[n].illegal_move = True
            else:
                vel_x, vel_y = 0, 0
                if new_px - x > 0: vel_x = 1
                elif new_px - x < 0: vel_x = -1
                if new_py - y > 0: vel_y = 1
                elif new_py - y < 0: vel_y = -1

                self.players[n].vel = vel_x, vel_y

            self.players[n].x, self.players[n].y = new_px, new_py

    def to_coords(self, x, y):
        return (
            math.floor(x / self.block_size),
            math.floor(y / self.block_size)
        )

    def to_pixels(self, x, y):
        return (
            math.floor(x * self.block_size),
            math.floor(y * self.block_size)
        )
