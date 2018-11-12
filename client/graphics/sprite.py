from __future__ import division
import os
import math
import pygame

from client_config import FRAME_RATE, BLOCKS_PER_SEC
# max updates to server per second (also move speed in coords)
import config

# globals
DIR = os.path.dirname(os.path.realpath(__file__))
FRAMES_PER_TICK = FRAME_RATE / BLOCKS_PER_SEC # float
SPRITE_UPDATE_INTERVAL = math.floor(FRAME_RATE / 8)

class Sprite(pygame.sprite.Sprite):
    def __init__(self, game, player, block_size, walls):
        pygame.sprite.Sprite.__init__(self)

        self.pixels_per_frame =  block_size * BLOCKS_PER_SEC / FRAME_RATE
        self.player = player
        self.block_size = block_size
        self.res = game.maze.width * block_size
        self.walls = walls

        get_image = lambda n: os.path.join(DIR, 'sprites/sprites/elf_f_run_anim_f' + str(n) + '.png')
        self.images = []
        for n in range(0, 4):
            self.images.append(pygame.image.load(get_image(n)))
        self.image_number = 0
        self.image = self.images[self.image_number]
        self.update_sprite = 1 # when it's 0, update sprite

        self.x_offset = self.image.get_width() / 2
        self.y_offset = self.image.get_height() * 0.75

        self.radius = self.block_size / 2 # pixels to center
        self.x = player.x * block_size + self.radius # pixel position
        self.y = player.y * block_size + self.radius
        self.rect = pygame.Rect(round(self.x - self.x_offset), round(self.y - self.y_offset),
                                self.image.get_width(), self.image.get_height())

        self.prio = 'x'

    def update(self):
        if self.update_sprite == 0:
            self.image_number = (self.image_number + 1) % 4
            self.image = self.images[self.image_number]
        self.update_sprite = (self.update_sprite + 1) % SPRITE_UPDATE_INTERVAL

        if self.player.local:
            if self.player.illegal_move:
                self.player.illegal_move = False
                (self.x, self.y) = self.to_pixels((self.player.x, self.player.y))
                (self.x, self.y) = (self.x + self.radius, self.y + self.radius)
            else:
                self.handle_collision()
        else:
            (realX, realY) = self.to_pixels((self.player.x, self.player.y))
            self.x = self.x + (realX - self.x) / FRAMES_PER_TICK
            self.y = self.y + (realY - self.y) / FRAMES_PER_TICK

        self.rect[0], self.rect[1] = (round(self.x - self.x_offset),
                                      round(self.y - self.y_offset))

    def handle_collision(self):
        # New x, y
        new_x = self.x + self.pixels_per_frame * self.player.vel[0]
        new_y = self.y + self.pixels_per_frame * self.player.vel[1]

        # Check if new x,y is within the map
        if new_x - self.radius < 0:
            new_x = self.radius
        elif new_x + self.radius > self.res:
            new_x = self.res - self.radius
        if new_y - self.radius < 0:
            new_y = self.radius
        elif new_y + self.radius > self.res:
            new_y = self.res - self.radius

        def make_rect(x, y):
            return pygame.Rect(x - self.radius, y - self.radius,
                                self.block_size, self.block_size)

        bounding_rect = make_rect(new_x, new_y)

        wall = bounding_rect.collidelist(self.walls)
        if not wall == -1:
            if make_rect(self.x, new_y).collidelist(self.walls) == -1:
                new_x = self.x
            elif make_rect(new_x, self.y).collidelist(self.walls) == -1:
                new_y = self.y
            else:
                new_x, new_y = self.x, self.y

        self.x, self.y = new_x, new_y

        new_pos = self.to_coords((self.x, self.y))
        if new_pos[0] != self.player.x and new_pos[1] != self.player.y:
            # can't move in both x and y direction at the same time
            if self.prio == 'x':
                self.player.x = new_pos[0]
                self.prio = 'y'
            else:
                self.player.y = new_pos[1]
                self.prio = 'x'

        elif new_pos != (self.player.x, self.player.y):
            self.player.x, self.player.y = new_pos

    def to_pixels(self, coords):
        return (
            math.floor(coords[0] * self.block_size),
            math.floor(coords[1] * self.block_size)
        )

    def to_coords(self, pixels):
        return (
            math.floor(pixels[0] / self.block_size),
            math.floor(pixels[1] / self.block_size)
        )
