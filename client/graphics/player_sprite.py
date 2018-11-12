from __future__ import division
import os
import math
import pygame
from .animated_sprite import AnimatedSprite

from client_config import FRAME_RATE, BLOCKS_PER_SEC
# max updates to server per second (also move speed in coords)
import config

# globals
DIR = os.path.dirname(os.path.realpath(__file__))
FRAMES_PER_TICK = FRAME_RATE / BLOCKS_PER_SEC # float
SPRITE_UPDATE_INTERVAL = math.floor(FRAME_RATE / 8)
PLAYER_SPRITE_WIDTH = 16
PLAYER_SPRITE_HEIGHT = 28

class PlayerSprite(AnimatedSprite):
    def __init__(self, game, player, block_size, walls, sprite):
        get_image = lambda n: os.path.join(DIR, 'sprites/sprites/' + sprite + '_run_anim_f' + str(n) + '.png')
        images = []
        for i in range(4):
            images.append(get_image(i))
        
        # Scale sprites
        size_margin = 1  # make the character slightly bigger - looks nicer
        scaling_factor = block_size / PLAYER_SPRITE_WIDTH
        new_dimensions = (
            math.floor(block_size * size_margin),
            math.floor(PLAYER_SPRITE_HEIGHT * scaling_factor * size_margin))

        # Sprite offsets
        x_offset = -2 * scaling_factor * size_margin    # the sprite should be moved about 2 pixels to the right
        y_offset = 12 * scaling_factor * size_margin    # move 12 pixels up

        AnimatedSprite.__init__(self, images, (
            player.x * block_size, 
            player.y * block_size,
            new_dimensions[0],
            new_dimensions[1]
        ), (x_offset, y_offset))

        # Generate leftwards-facing images
        self.images_right = self.images
        self.images_left = []
        for image in self.images_right:
            self.images_left.append(pygame.transform.flip(image, True, False))

        self.pixels_per_frame = block_size * BLOCKS_PER_SEC / FRAME_RATE
        self.player = player
        self.block_size = block_size
        self.res = game.maze.width * block_size
        self.walls = walls

        self.moving_right = True

        self.radius = self.block_size / 2 # pixels to center

        self.prio = 'x'

    def update(self):
        AnimatedSprite.update(self)
        if self.player.local:
            if self.player.vel[0] < 0 and self.moving_right:
                self.images = self.images_left
                self.flip_direction()
            elif self.player.vel[0] > 0 and not self.moving_right:
                self.images = self.images_right
                self.flip_direction()

            if self.player.illegal_move:
                self.player.illegal_move = False
                (self.x, self.y) = self.to_pixels((self.player.x, self.player.y))
            else:
                self.handle_collision()
        else:
            (realX, realY) = self.to_pixels((self.player.x, self.player.y))
            self.x = self.x + (realX - self.x) / FRAMES_PER_TICK
            self.y = self.y + (realY - self.y) / FRAMES_PER_TICK

        self.rect[0], self.rect[1] = (math.floor(self.x - self.x_offset),
                                      math.floor(self.y - self.y_offset))

    def flip_direction(self):
        self.moving_right = not self.moving_right
        self.x_offset = -self.x_offset
        self.next_image()

    def handle_collision(self):
        # New x, y
        new_x = self.x + self.pixels_per_frame * self.player.vel[0]
        new_y = self.y + self.pixels_per_frame * self.player.vel[1]

        # Check if new x,y is within the map
        if new_x < 0:
            new_x = 0
        elif new_x >= self.res - self.block_size:
            new_x = self.res - 1
        if new_y < 0:
            new_y = 0
        elif new_y  > self.res - self.block_size:
            new_y = self.res - 1

        def make_rect(x, y):
            return pygame.Rect(x, y,
                                self.block_size, self.block_size)

        bounding_rect = make_rect(new_x, new_y)

        wall = bounding_rect.collidelist(self.walls)
        if not wall == -1:
            if make_rect(self.x, new_y).collidelist(self.walls) == -1:
                new_x = self.round_pixel(self.x + self.radius)
            elif make_rect(new_x, self.y).collidelist(self.walls) == -1:
                new_y = self.round_pixel(self.y + self.radius)
            else:
                new_x, new_y = self.x, self.y

        self.x, self.y = new_x, new_y

        new_pos = self.to_coords((self.x + self.radius, self.y + self.radius))
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

    def round_pixel(self, pixel):
        return math.floor(pixel / self.block_size) * self.block_size
