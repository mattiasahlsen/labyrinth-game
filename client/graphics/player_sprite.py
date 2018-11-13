from __future__ import division
import os
import math
import pygame
from .animated_sprite import AnimatedSprite

# max updates to server per second (also move speed in coords)
import client_config

# globals
DIR = os.path.dirname(os.path.realpath(__file__))
<<<<<<< HEAD
=======
SPRITE_UPDATE_INTERVAL = math.floor(client_config.FRAME_RATE / 8)
>>>>>>> b5579240c0ad18ec21a89f325dbab1b66aa022bf
PLAYER_SPRITE_WIDTH = 16
PLAYER_SPRITE_HEIGHT = 28

class PlayerSprite(AnimatedSprite):
<<<<<<< HEAD
    def __init__(self, player, block_size, sprite):
        get_image = lambda n: os.path.join(DIR, 'sprites/sprites/' + sprite + '_run_anim_f' + str(n) + '.png')
=======
    def __init__(self, player, block_size, img):
        get_image = lambda n: os.path.join(DIR, 'sprites/sprites/' + img + '_run_anim_f' + str(n) + '.png')
>>>>>>> b5579240c0ad18ec21a89f325dbab1b66aa022bf
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
<<<<<<< HEAD
            player.px,
            player.py,
=======
            player.x * block_size,
            player.y * block_size,
>>>>>>> b5579240c0ad18ec21a89f325dbab1b66aa022bf
            new_dimensions[0],
            new_dimensions[1]
        ), (x_offset, y_offset))

        # Generate leftwards-facing images
        self.images_right = self.images
        self.images_left = []
        for image in self.images_right:
            self.images_left.append(pygame.transform.flip(image, True, False))

        self.player = player
        self.block_size = block_size

        self.moving_right = True
<<<<<<< HEAD
=======
        self.radius = self.block_size / 2 # pixels to center
>>>>>>> b5579240c0ad18ec21a89f325dbab1b66aa022bf
        self.prio = 'x'

    def update(self):
        AnimatedSprite.update(self)
<<<<<<< HEAD
        if self.player.local:
            if self.player.vel[0] < 0 and self.moving_right:
                self.images = self.images_left
                self.flip_direction()
            elif self.player.vel[0] > 0 and not self.moving_right:
                self.images = self.images_right
                self.flip_direction()

        self.x = self.player.px
        self.y = self.player.py
        self.rect[0] = math.floor(self.x - self.x_offset)
        self.rect[1] = math.floor(self.y - self.y_offset)
=======

        if self.player.vel[0] < 0 and self.moving_right:
            self.flip_direction()
        elif self.player.vel[0] > 0 and not self.moving_right:
            self.flip_direction()

        self.rect.x  = math.floor(self.x - self.x_offset)
        self.rect.y =  math.floor(self.y - self.y_offset)
>>>>>>> b5579240c0ad18ec21a89f325dbab1b66aa022bf

    def flip_direction(self):
        self.moving_right = not self.moving_right
        self.x_offset = -self.x_offset
        self.next_image()
        if self.images is self.images_right:
            self.images = self.images_left
        else:
            self.images = self.images_right

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
