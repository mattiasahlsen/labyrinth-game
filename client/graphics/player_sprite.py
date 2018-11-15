from __future__ import division
import os
import math
import pygame
from .animated_sprite import AnimatedSprite

# max updates to server per second (also move speed in coords)
import client_config

# globals
DIR = os.path.dirname(os.path.realpath(__file__))
PLAYER_SPRITE_WIDTH = 16
PLAYER_SPRITE_HEIGHT = 28

# Sprite sets dict keys
RUN_RIGHT = 'run_right'
RUN_LEFT = 'run_left'
IDLE_RIGHT = 'idle_right'
IDLE_LEFT = 'idle_left'

class PlayerSprite(AnimatedSprite):
    def __init__(self, player, block_size, img):
        def get_image(n, type_):
            return os.path.join(DIR, 'sprites/sprites/' + img + type_ + str(n) + '.png')
        run = []
        idle = []
        for i in range(4):
            run.append(get_image(i, '_run_anim_f'))
            idle.append(get_image(i, '_idle_anim_f'))
        image_dict = dict([(RUN_RIGHT, run), (IDLE_RIGHT, idle)])

        # Scale sprites
        size_margin = 1  # make the character slightly bigger - looks nicer
        scaling_factor = block_size / PLAYER_SPRITE_WIDTH
        new_dimensions = (
            math.floor(block_size * size_margin),
            math.floor(PLAYER_SPRITE_HEIGHT * scaling_factor * size_margin))

        # Sprite offsets
        x_offset = -2 * scaling_factor * size_margin    # the sprite should be moved about 2 pixels to the right
        y_offset = 12 * scaling_factor * size_margin    # and 12 pixels up

        AnimatedSprite.__init__(self, image_dict, (
            player.px,
            player.py,
            new_dimensions[0],
            new_dimensions[1]
        ), (x_offset, y_offset))

        # Generate left-facing images
        run_left = []
        idle_left = []
        for image in self.image_sets[RUN_RIGHT]:
            run_left.append(pygame.transform.flip(image, True, False))
        for image in self.image_sets[IDLE_RIGHT]:
            idle_left.append(pygame.transform.flip(image, True, False))

        self.image_sets[RUN_LEFT] = run_left
        self.image_sets[IDLE_LEFT] = idle_left

        self.player = player
        self.block_size = block_size

        self.facing_right = True
        self.moving = True

    def update(self, root_x, root_y):
        AnimatedSprite.update(self)
        if self.player.vel[0] < 0 and self.facing_right:
            self.flip_direction()
        elif self.player.vel[0] > 0 and not self.facing_right:
            self.flip_direction()
        elif self.player.vel[0] == 0 and self.player.vel[1] == 0 and self.moving:
            self.toggle_idle()
        elif (self.player.vel[0] != 0 or self.player.vel[1] != 0) and not self.moving:
            self.toggle_idle()

        self.x = self.player.px - root_x
        self.y = self.player.py - root_y
        self.rect[0] = math.floor(self.x - self.x_offset)
        self.rect[1] = math.floor(self.y - self.y_offset)

    def toggle_idle(self):
        self.moving = not self.moving
        if self.current_set_key == IDLE_LEFT or self.current_set_key == IDLE_RIGHT:
            if self.facing_right:
                img_set = RUN_RIGHT
            else:
                img_set = RUN_LEFT
        else:
            if self.facing_right:
                img_set = IDLE_RIGHT
            else:
                img_set = IDLE_LEFT

        self.switch_image_set(img_set)
        self.next_image()

    def flip_direction(self):
        self.facing_right = not self.facing_right
        self.x_offset = -self.x_offset
        if self.current_set_key == RUN_RIGHT or self.current_set_key == IDLE_RIGHT:
            if self.moving:
                img_set = RUN_LEFT
            else:
                img_set = IDLE_LEFT
        else:
            if self.moving:
                img_set = RUN_RIGHT
            else:
                img_set = IDLE_RIGHT

        self.switch_image_set(img_set)
        self.next_image()

    def to_pixels(self, coords):
        return (
            math.floor(coords[0] * self.block_size),
            math.floor(coords[1] * self.block_size)
        )
