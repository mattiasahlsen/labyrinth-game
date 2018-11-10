from __future__ import division
import os
import math
import pygame

from client_config import FRAME_RATE, BLOCKS_PER_SEC
from config import TICK_RATE # updates from server per second

# globals
DIR = os.path.dirname(os.path.realpath(__file__))
FRAMES_PER_TICK = FRAME_RATE / TICK_RATE # float

class Sprite(pygame.sprite.Sprite):
    def __init__(self, game, player, block_size):
        pygame.sprite.Sprite.__init__(self)

        # should be a float
        self.pixels_per_frame =  block_size * BLOCKS_PER_SEC / FRAME_RATE

        self.game = game
        self.player = player
        self.block_size = block_size

        self.x = player.x * block_size # pixel position
        self.y = player.y * block_size

        get_image = lambda n: os.path.join(DIR, 'sprites/sprites/elf_f_run_anim_f' + str(n) + '.png')
        self.images = []
        for n in range(0, 4):
            self.images.append(get_image(n))
        self.image_number = 0
        self.image = self.images[self.image_number]

        self.rect = pygame.Rect(self.player.x, self.player.y, block_size, block_size)

    def update(self):
        self.image_number = (self.image_number + 1) % 4
        self.image = self.image[self.image_number]

        if self.player.local:
            if self.player.illegal_move:
                self.player.illegal_move = False
                self.x = self.player.x * self.block_size
                self.y = self.player.y * self.block_size

                self.rect = pygame.Rect(self.x, self.y,
                                        self.block_size, self.block_size)

            else:
                self.x += self.pixels_per_frame * self.vel[0]
                self.y += self.pixels_per_frame * self.vel[1]
                self.rect = pygame.Rect(round(self.x), round(self.y),
                                        self.block_size, self.block_size)
        else:
            (realX, realY) = to_pixels((self.player.x, self.player.y))
            self.x = (realX - self.x) / FRAMES_PER_TICK
            self.y = (realy - self.y) / FRAMES_PER_TICK
            self.rect = pygame.Rect(round(self.x), round(self.y)
                                    self.block_size, self.block_size)

    def to_pixels(self, coords):
        return (
            math.floor(coords[0] / self.block_size),
            math.floor(coords[1] / self.block_size)
        )
    def to_coords(self, pixels):
        return (
            math.floor(pixels[0] / * self.block_size),
            math.floor(pixels[1] / * self.block_size)
        )
